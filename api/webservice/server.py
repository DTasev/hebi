import os
import os.path

import json_tricks
import voluptuous
from flask import Flask, jsonify, request, abort, send_file
from flask.json import JSONEncoder
from flask_api import status
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from scripts.config_generator.content import Content

import const
import validation
from apps import plugins, run
from execution import NoSuchJobError
from utils import (plugin_list_entry_to_dict,
                   is_file_a_data_file, is_file_a_process_list, validate_file,
                   create_process_list_from_user_data,
                   find_files_recursive)


class BetterJsonEncoder(JSONEncoder):
    def default(self, o):
        return json_tricks.dumps(o)


app = Flask('savu')
app.json_encoder = BetterJsonEncoder
socketio = SocketIO(app)
CORS(app)

plugins.register(app)
run.register(app)


def setup_runners():
    import importlib
    for queue_name, runner in app.config[const.CONFIG_NAMESPACE_SAVU][
        const.CONFIG_KEY_JOB_RUNNERS].iteritems():
        # Create an instance of the job runner
        m = importlib.import_module(runner[const.CONFIG_KEY_RUNNER_MODULE])
        c = getattr(m, runner[const.CONFIG_KEY_RUNNER_CLASS])
        params = runner[const.CONFIG_KEY_RUNNER_PARAMETERS]
        runner[const.CONFIG_KEY_RUNNER_INSTANCE] = c(**params)

        def send_updates_thread_fun(qn, runner):
            """
            Function which loops forever and periodically sends out job status updates
            TODO: check if the job status has actually changed before sending an update
            """
            while True:
                for job_id, job in runner._jobs.items():
                    ws_send_job_status(qn, job_id)
                socketio.sleep(2)

        socketio.start_background_task(send_updates_thread_fun, queue_name,
                                       runner[const.CONFIG_KEY_RUNNER_INSTANCE])


def teardown_runners():
    for _, v in app.config[const.CONFIG_NAMESPACE_SAVU][const.CONFIG_KEY_JOB_RUNNERS]:
        v[const.CONFIG_KEY_RUNNER_INSTANCE].close()


def validate_config():
    validation.server_configuration_schema(
        app.config[const.CONFIG_NAMESPACE_SAVU])


@app.route('/process_list')
def process_list_list():
    # Listing process list files in a given search directory
    if const.KEY_PATH in request.args:
        # Get the absolute path being searched
        user_path = request.args.get(const.KEY_PATH)
        abs_path = os.path.abspath(os.path.expanduser(user_path))

        data = {
            const.KEY_PATH: abs_path,
            const.KEY_FILES: list(
                find_files_recursive(abs_path, is_file_a_process_list)),
        }

        validation.filename_listing_schema(data)
        return jsonify(data)

    # Listing details of a specific process list
    elif const.KEY_FILENAME in request.args:
        fname = request.args.get(const.KEY_FILENAME)

        # Ensure file is a valid process list
        if not validate_file(fname, is_file_a_process_list):
            abort(status.HTTP_404_NOT_FOUND)

        # Open process list
        process_list = Content()
        process_list.fopen(fname)

        # Format plugin list
        plugins = [plugin_list_entry_to_dict(p) for \
                   p in process_list.plugin_list.plugin_list]

        data = {const.KEY_FILENAME: fname, const.KEY_PLUGINS: plugins}

        validation.process_list_list_filename_schema(data)
        return jsonify(data)

    else:
        abort(status.HTTP_400_BAD_REQUEST)


@app.route('/process_list', methods=['POST'])
def process_list_create():
    fname = request.args.get(const.KEY_FILENAME)

    # Ensure file does not already exist
    if validate_file(fname, is_file_a_process_list):
        abort(status.HTTP_409_CONFLICT)

    # Get user supplied JSON and validate it
    user_pl_data = request.get_json()
    try:
        validation.process_list_update_schema(user_pl_data)
    except voluptuous.error.Error:
        abort(status.HTTP_400_BAD_REQUEST)

    # Create new process list
    process_list = create_process_list_from_user_data(user_pl_data)

    # Save process list
    process_list.save(fname)

    # Handle process list view
    return process_list_list()


@app.route('/process_list', methods=['PUT'])
def process_list_update():
    fname = request.args.get(const.KEY_FILENAME)

    # Get user supplied JSON and validate it
    user_pl_data = request.get_json()
    try:
        validation.process_list_update_schema(user_pl_data)
    except voluptuous.error.Error:
        abort(status.HTTP_400_BAD_REQUEST)

    # Create new process list
    process_list = create_process_list_from_user_data(user_pl_data)

    # Delete existing process list
    process_list_delete()

    # Save new process list
    process_list.save(fname)

    # Handle process list view
    return process_list_list()


@app.route('/process_list', methods=['DELETE'])
def process_list_delete():
    fname = request.args.get(const.KEY_FILENAME)

    # Ensure file is a valid process list
    if not validate_file(fname, is_file_a_process_list):
        abort(status.HTTP_404_NOT_FOUND)

    # Delete file
    os.remove(fname)

    data = {
        const.KEY_FILENAME: fname,
    }

    validation.process_list_delete_schema(data)
    return jsonify(data)


@app.route('/process_list/download')
def process_list_download():
    fname = request.args.get(const.KEY_FILENAME)

    # Ensure file is a valid process list
    if not validate_file(fname, is_file_a_process_list):
        abort(status.HTTP_404_NOT_FOUND)

    return send_file(fname)


@app.route('/data/find')
def data_find():
    user_path = request.args.get(const.KEY_PATH)
    if not user_path:
        return abort(status.HTTP_400_BAD_REQUEST)

    # Get the absolute path being searched
    abs_path = os.path.abspath(os.path.expanduser(user_path))

    data = {
        const.KEY_PATH: abs_path,
        const.KEY_FILES: list(
            find_files_recursive(abs_path, is_file_a_data_file)),
    }

    validation.filename_listing_schema(data)
    return jsonify(data)


@app.route('/jobs/<queue>/submit')
def jobs_queue_submit(queue):
    dataset = request.args.get(const.KEY_DATASET)
    process_list = request.args.get(const.KEY_PROCESS_LIST_FILE)
    output = request.args.get(const.KEY_OUTPUT_PATH)

    # Ensure file is a valid dataset
    if not validate_file(dataset, is_file_a_data_file):
        abort(status.HTTP_404_NOT_FOUND)

    # Ensure file is a valid process list
    if not validate_file(process_list, is_file_a_process_list):
        abort(status.HTTP_404_NOT_FOUND)

    # Start job
    job = app.config[const.CONFIG_NAMESPACE_SAVU][
        const.CONFIG_KEY_JOB_RUNNERS][queue][
        const.CONFIG_KEY_RUNNER_INSTANCE].start_job(dataset, process_list,
                                                    output)

    return jobs_queue_info(queue, job)


@app.route('/jobs/<queue_name>/<job_id>')
def jobs_queue_info(queue_name, job_id):
    queue = app.config[const.CONFIG_NAMESPACE_SAVU][
        const.CONFIG_KEY_JOB_RUNNERS].get(queue_name)
    if queue is None:
        abort(status.HTTP_404_NOT_FOUND)

    try:
        data = {
            const.KEY_QUEUE_ID: queue_name,
            const.KEY_JOB_ID: queue[const.CONFIG_KEY_RUNNER_INSTANCE].job(
                job_id).to_dict(),
        }

        validation.jobs_queue_info_schema(data)
        return jsonify(data)

    except NoSuchJobError:
        abort(status.HTTP_404_NOT_FOUND)


@app.route('/default_paths')
def data_default_path():
    data = {}

    def get_path(ns, key):
        data[key] = app.config[const.CONFIG_NAMESPACE_SAVU][ns]['default']

    get_path('data_location', 'data')
    get_path('process_list_location', 'process_list')
    get_path('output_location', 'output')

    return jsonify(data)


def ws_send_job_status(queue_name, job_id):
    queue = app.config[const.CONFIG_NAMESPACE_SAVU]['job_runners'].get(
        queue_name)
    data = {
        const.KEY_QUEUE_ID: queue_name,
        const.KEY_JOB_ID: queue['instance'].job(job_id).to_dict(),
    }

    validation.jobs_queue_info_schema(data)

    room = queue_name + '/' + job_id
    socketio.emit(
        const.EVENT_JOB_STATUS,
        data,
        room=room,
        namespace=const.WS_NAMESPACE_JOB_STATUS)


@socketio.on('join', namespace=const.WS_NAMESPACE_JOB_STATUS)
def ws_on_join_job_status(data):
    room = data[const.KEY_QUEUE_ID] + '/' + data[const.KEY_JOB_ID]
    join_room(room)
    # Send an update now to ensure client is up to date
    ws_send_job_status(data[const.KEY_QUEUE_ID], data[const.KEY_JOB_ID])


@socketio.on('leave', namespace=const.WS_NAMESPACE_JOB_STATUS)
def ws_on_leave_job_status(data):
    room = data[const.KEY_QUEUE_ID] + '/' + data[const.KEY_JOB_ID]
    leave_room(room)
