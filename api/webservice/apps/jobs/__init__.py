from flask import jsonify, request, abort
from flask_api import status

from webservice import const
from webservice.apps.common.utils import is_file_a_data_file, is_file_a_process_list, validate_file
from webservice.apps.jobs import urlparams, validation
from webservice.execution import NoSuchJobError


def register(app):
    @app.route('/jobs/<queue>/submit')
    def jobs_queue_submit(queue):
        dataset = request.args.get(urlparams.KEY_DATASET)
        process_list = request.args.get(urlparams.KEY_PROCESS_LIST_FILE)
        output = request.args.get(urlparams.KEY_OUTPUT_PATH)

        # Ensure file is a valid dataset
        if not validate_file(dataset, is_file_a_data_file):
            abort(status.HTTP_404_NOT_FOUND)

        # Ensure file is a valid process list
        if not validate_file(process_list, is_file_a_process_list):
            abort(status.HTTP_404_NOT_FOUND)

        # Start job
        job = app.config[const.CONFIG_NAMESPACE_SAVU][
            const.CONFIG_KEY_JOB_RUNNERS][queue][
            const.CONFIG_KEY_RUNNER_INSTANCE].start_job(dataset, process_list, output)

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
