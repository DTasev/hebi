import os

from flask import request

from webservice.apps.run import urls
from webservice.apps.run.postparams import PROCESS_LIST_FILE, PROCESS_LIST_NAME


def register(app):
    @app.route(urls.RUN, methods=["POST"])
    def run_plugin():
        import pydevd
        pydevd.settrace('localhost', port=6969, stdoutToServer=True, stderrToServer=True)

        if PROCESS_LIST_FILE in request.files and PROCESS_LIST_NAME in request.form:
            request.files[PROCESS_LIST_FILE].save(os.path.expanduser("~/{}".format(request.form[PROCESS_LIST_NAME])))
            ret_val = "File saved!"
        else:
            ret_val = "Not saved."
        return ret_val
