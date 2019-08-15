import json

import json_tricks
from flask import Flask, jsonify
from flask.json import JSONEncoder
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room

import const
import validation


class BetterJsonEncoder(JSONEncoder):
    def default(self, o):
        return json_tricks.dumps(o)


app = Flask('savu')
app.json_encoder = BetterJsonEncoder
socketio = SocketIO(app, logger=True, engineio_logger=True,
                    cors_allowed_origins="*")
CORS(app)

# can't import socketio unless this is imported after socketio has been created
# TODO fix this silly dependency
from webservice.apps import plugins, process_list, jobs

plugins.register(app)
# job.register(app)
process_list.register(app)
jobs.register(app)


def setup_runners():
    import importlib
    for queue_name, runner in app.config[const.CONFIG_NAMESPACE_SAVU][
        const.CONFIG_KEY_JOB_RUNNERS].iteritems():
        # Create an instance of the job runner
        m = importlib.import_module(runner[const.CONFIG_KEY_RUNNER_MODULE])
        c = getattr(m, runner[const.CONFIG_KEY_RUNNER_CLASS])
        params = runner[const.CONFIG_KEY_RUNNER_PARAMETERS]
        runner[const.CONFIG_KEY_RUNNER_INSTANCE] = c(**params)

        # def send_updates_thread_fun(qn, runner):
        #     """
        #     Function which loops forever and periodically sends out job status updates
        #     TODO: check if the job status has actually changed before sending an update
        #     """
        #     while True:
        #         for job_id, job in runner._jobs.items():
        #             ws_send_job_status(qn, job_id)
        #         socketio.sleep(2)
        #
        # socketio.start_background_task(send_updates_thread_fun, queue_name,
        #                                runner[const.CONFIG_KEY_RUNNER_INSTANCE])


def teardown_runners():
    for _, v in app.config[const.CONFIG_NAMESPACE_SAVU][const.CONFIG_KEY_JOB_RUNNERS]:
        v[const.CONFIG_KEY_RUNNER_INSTANCE].close()


def validate_config():
    validation.server_configuration_schema(app.config[const.CONFIG_NAMESPACE_SAVU])


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
    queue = app.config[const.CONFIG_NAMESPACE_SAVU]['job_runners'].get(queue_name)
    data = {
        const.KEY_QUEUE_ID: queue_name,
        const.KEY_JOB_ID: queue['instance'].job(job_id).to_dict(),
    }
    from webservice.apps.jobs import validation

    validation.jobs_queue_info_schema(data)

    room = queue_name + '/' + job_id
    socketio.emit(const.EVENT_JOB_RADIO,
                  data,
                  room=room,
                  namespace=const.WS_NAMESPACE_JOB_STATUS)


# def setInterval(func, time):
#     e = threading.Event()
#     while setInterval.times != 0 and not e.wait(time):
#         func(setInterval.times)
#         setInterval.times -= 1
#
#
# setInterval.times = 10
#
#
# def foo(num_left):
#     socketio.emit(
#         const.EVENT_JOB_STATUS,
#         "Calling {} more times".format(num_left),
#         room='0/0',
#         namespace=const.WS_NAMESPACE_JOB_STATUS)


@socketio.on('join', namespace=const.WS_NAMESPACE_JOB_STATUS)
def ws_on_join_job_status(data):
    data = json.loads(data)
    room = "{}/{}".format(data[const.KEY_QUEUE_ID], data[const.KEY_JOB_ID])
    join_room(room)
    # Send an update now to ensure client is up to date


#     ws_send_job_status(data[const.KEY_QUEUE_ID], data[const.KEY_JOB_ID])
#     setInterval.times = 10
#     setInterval(foo, 1)


@socketio.on('leave', namespace=const.WS_NAMESPACE_JOB_STATUS)
def ws_on_leave_job_status(data):
    room = data[const.KEY_QUEUE_ID] + '/' + data[const.KEY_JOB_ID]
    leave_room(room)
