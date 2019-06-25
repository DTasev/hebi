import os
import os.path

import voluptuous
from flask import jsonify, request, abort, send_file
from flask_api import status
from scripts.config_generator.content import Content

from webservice.apps.common.utils import validate_file, is_file_a_process_list
from webservice.apps.process_list import urlparams
from webservice.apps.process_list import urls
from webservice.apps.process_list import validation
from webservice.apps.process_list.utils import find_files_recursive, plugin_list_entry_to_dict, \
    create_process_list_from_user_data


def register(app):
    @app.route(urls.PROCESS_LIST)
    def process_list_list():
        # Listing process list files in a given search directory
        if urlparams.KEY_PATH in request.args:
            # Get the absolute path being searched
            user_path = request.args.get(urlparams.KEY_PATH)
            abs_path = os.path.abspath(os.path.expanduser(user_path))

            data = {
                urlparams.KEY_PATH: abs_path,
                urlparams.KEY_FILES: list(
                    find_files_recursive(abs_path, is_file_a_process_list)),
            }

            validation.filename_listing_schema(data)
            return jsonify(data)

        # Listing details of a specific process list
        elif urlparams.KEY_FILENAME in request.args:
            fname = request.args.get(urlparams.KEY_FILENAME)

            # Ensure file is a valid process list
            if not validate_file(fname, is_file_a_process_list):
                abort(status.HTTP_404_NOT_FOUND)

            # Open process list
            process_list = Content()
            process_list.fopen(fname)

            # Format plugin list
            plugins = [plugin_list_entry_to_dict(p) for \
                       p in process_list.plugin_list.plugin_list]

            data = {urlparams.KEY_FILENAME: fname, urlparams.KEY_PLUGINS: plugins}

            validation.process_list_list_filename_schema(data)
            return jsonify(data)

        else:
            abort(status.HTTP_400_BAD_REQUEST)

    @app.route(urls.PROCESS_LIST, methods=['POST'])
    def process_list_create():
        fname = request.args.get(urlparams.KEY_FILENAME)

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

    @app.route(urls.PROCESS_LIST, methods=['PUT'])
    def process_list_update():
        fname = request.args.get(urlparams.KEY_FILENAME)

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

    @app.route(urls.PROCESS_LIST, methods=['DELETE'])
    def process_list_delete():
        fname = request.args.get(urlparams.KEY_FILENAME)

        # Ensure file is a valid process list
        if not validate_file(fname, is_file_a_process_list):
            abort(status.HTTP_404_NOT_FOUND)

        # Delete file
        os.remove(fname)

        data = {
            urlparams.KEY_FILENAME: fname,
        }

        validation.process_list_delete_schema(data)
        return jsonify(data)

    @app.route(urls.PROCESS_LIST_DOWNLOAD)
    def process_list_download():
        fname = request.args.get(urlparams.KEY_FILENAME)

        # Ensure file is a valid process list
        if not validate_file(fname, is_file_a_process_list):
            abort(status.HTTP_404_NOT_FOUND)

        return send_file(fname)
