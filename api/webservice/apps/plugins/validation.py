from voluptuous import Schema, Required, ALLOW_EXTRA

from webservice.apps.common.validation import any_string, any_non_empty_string, citation, parameter_full

get_plugin_info_schema = Schema({
    Required('name'): any_non_empty_string,
    Required('info'): any_string,
    Required('synopsis'): any_string,
    Required('warn'): any_string,
    Required('id'): any_non_empty_string,
    Required('citation'): [citation],
    Required('parameters'): [parameter_full],
})
query_plugin_list_with_details_schema = Schema({
    Required(any_non_empty_string): get_plugin_info_schema
}, extra=ALLOW_EXTRA)

query_plugin_list_schema = Schema([any_non_empty_string], extra=ALLOW_EXTRA)
