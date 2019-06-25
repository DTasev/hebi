from voluptuous import Schema, Required

from webservice.apps.common.validation import any_non_empty_string, any_string, citation, \
    parameter_full, parameter_basic

_plugin_basic = {
    Required('name'): any_non_empty_string,
    Required('active'): bool,
    Required('parameters'): [parameter_basic],
}

_plugin_full = {
    Required('name'): any_non_empty_string,
    Required('active'): bool,
    Required('info'): any_string,
    Required('synopsis'): any_string,
    Required('warn'): any_string,
    Required('citation'): [citation],
    Required('id'): any_non_empty_string,
    Required('parameters'): [parameter_full],
}

process_list_list_filename_schema = Schema({
    Required('filename'): any_non_empty_string,
    Required('plugins'): [_plugin_full],
})

process_list_update_schema = Schema({
    Required('plugins'): [_plugin_basic],
})

process_list_delete_schema = Schema({
    Required('filename'): any_non_empty_string,
})
filename_listing_schema = Schema({
    Required('path'): any_non_empty_string,
    Required('files'): [any_non_empty_string],
})
