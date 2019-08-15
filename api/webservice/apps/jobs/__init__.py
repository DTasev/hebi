import os

from flask import jsonify, request, abort
from flask_api import status

from webservice import const
from webservice.apps.common.utils import is_file_a_process_list, validate_file
from webservice.apps.jobs import urlparams, validation
from webservice.execution import NoSuchJobError


def save_process_list_locally(process_list, process_list_name):
    filepath = os.path.expanduser("~/{}.nxs".format(process_list_name))
    process_list.save(filepath)
    return filepath


def register(app):
    @app.route('/jobs/<queue>/submit', methods=["POST"])
    def jobs_queue_submit(queue):
        # import pydevd
        # pydevd.settrace('localhost', port=6969, stdoutToServer=True, stderrToServer=True)
        dataset = request.form.get(urlparams.KEY_DATASET)
        process_list = request.files.get(urlparams.KEY_PROCESS_LIST_FILE)
        process_list_name = request.form.get(urlparams.KEY_PROCESS_LIST_NAME)
        out_dir = "/output"
        try:
            process_list = save_process_list_locally(process_list, process_list_name)
        except Exception as e:
            return abort(jsonify(message="File not saved due to error: {}\n".format(e)), status.HTTP_404_NOT_FOUND)

        # Ensure file is a valid dataset
        if not os.path.isdir(os.path.abspath(dataset)):  # or not validate_file(dataset, is_file_a_data_file):
            return abort(jsonify(message="Failed to validate data provided as a valid folder path."),
                         status.HTTP_404_NOT_FOUND)
        # Ensure file is a valid process list
        if not validate_file(process_list, is_file_a_process_list):
            return abort(jsonify(message="Failed to validate process list as a valid HDF5 file."),
                         status.HTTP_404_NOT_FOUND)

        # Start job
        job_id = app.config[const.CONFIG_NAMESPACE_SAVU][
            const.CONFIG_KEY_JOB_RUNNERS][queue][
            const.CONFIG_KEY_RUNNER_INSTANCE].start_job(queue, dataset, process_list, out_dir)

        return jobs_queue_info(queue, job_id)

    @app.route('/jobs/<queue_name>/<job_id>')
    def jobs_queue_info(queue_name, job_id):
        queue = app.config[const.CONFIG_NAMESPACE_SAVU][
            const.CONFIG_KEY_JOB_RUNNERS].get(queue_name)
        if queue is None:
            abort(status.HTTP_404_NOT_FOUND)

        # check that the process started OK
        job = queue[const.CONFIG_KEY_RUNNER_INSTANCE].job(job_id)
        if not job.is_alive() and job.exit_code != 0:
            abort(jsonify(process_stdout=job.all_output()), status.HTTP_500_INTERNAL_SERVER_ERROR)

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
