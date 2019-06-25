import savu.plugins.utils as pu
from flask import jsonify, request, abort
from flask_api import status
from fuzzywuzzy import fuzz

from webservice.apps.plugins import urlparams
from webservice.apps.plugins import urls
from webservice.apps.plugins import validation
from webservice.utils import plugin_to_dict


def register(app):
    @app.route(urls.PLUGINS)
    def query_plugin_list():
        query = request.args.get(urlparams.KEY_QUERY)

        append_details = request.args.get(urlparams.KEY_DETAILS, default=False)
        if query:
            query = query.lower()
            plugin_names = [k for k, v in pu.plugins.iteritems()
                            if fuzz.partial_ratio(k.lower(), query) > 75]
        else:
            if append_details:
                plugin_names = {}
                for k, v in pu.plugins.viewitems():
                    plugin_names[k] = _get_plugin_info(k)

                validation.query_plugin_list_with_details_schema(plugin_names)
            else:
                plugin_names = [k for k, v in pu.plugins.iteritems()]
                validation.query_plugin_list_schema(plugin_names)

        return jsonify(plugin_names)

    @app.route('{}/<name>'.format(urls.PLUGINS))
    def get_plugin_info(name):
        """
        Returns the plugin info in JSON
        :param name: Name of the plugin for which the details are being retrieved
        :return:
        """
        if name not in pu.plugins:
            abort(status.HTTP_404_NOT_FOUND)

        data = _get_plugin_info(name)

        validation.get_plugin_info_schema(data)
        return jsonify(data)

    def _get_plugin_info(name):
        """
        Returns the plugin info as a Dict
        :param name:
        :return:
        """
        # Create plugin instance with default parameter values
        p = pu.plugins[name]()
        p._populate_default_parameters()
        data = plugin_to_dict(name, p)
        return data
