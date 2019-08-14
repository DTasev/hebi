import os

from flask import request, jsonify

from webservice.apps.job import urls
from webservice.apps.job.postparams import PROCESS_LIST_FILE, PROCESS_LIST_NAME, DATA_DIR
from webservice.apps.job.validation import job_run_schema
from webservice.execution.async_task import TalkativeSAVUProcess

jobs = {}


def register(app):
    @app.route("{}/{}".format(urls.JOB_NAMESPACE, urls.RUN), methods=["POST"])
    def run_plugin():
        # TODO make this better, using voluptuous or flask-inputs

        if PROCESS_LIST_FILE in request.files and PROCESS_LIST_NAME in request.form and DATA_DIR in request.form:
            response_data, status = run_plugin_success()
        else:
            response_data, status = run_plugin_fail()
        return jsonify(response_data), status

    def run_plugin_success():
        # start with OK code
        status = 200
        message = ""
        response_data = {}
        filepath = os.path.expanduser("~/{}".format(request.form[PROCESS_LIST_NAME]))
        try:
            request.files[PROCESS_LIST_FILE].save(filepath)
            message += "File saved.\n"
        except Exception as e:
            message += "File not saved due to error: {}\n".format(e)
            status = 400
            response_data = {"message": message}

        if os.path.isfile(filepath):
            try:
                out_dir = "/output"
                # TODO make this not 5
                job = TalkativeSAVUProcess(request.form[DATA_DIR], filepath, out_dir)
                jobs[job.id] = job
                job.start()
                message += "Process started."
                response_data = {"job_id": job.id, "message": message, "output_dir": out_dir}
            except Exception as e:
                message += "Process not started due to error: {}".format(e)
                status = 500
                response_data = {"message": message}
        return response_data, status

    def run_plugin_fail():
        message = "Not saved. Reason: "
        if PROCESS_LIST_FILE not in request.files:
            message += "Missing '{}' in files".format(PROCESS_LIST_FILE)
        if PROCESS_LIST_NAME not in request.form:
            message += "Missing '{}' in form".format(PROCESS_LIST_NAME)
        if DATA_DIR not in request.form:
            message += "Missing '{}' in form".format(DATA_DIR)
        response_data = {"message": message}
        status = 400
        return response_data, status
