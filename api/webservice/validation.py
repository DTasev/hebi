from voluptuous import Schema, Required, All, Any, Length, Extra

from webservice.apps.common.validation import citation, parameter_basic, parameter_full

_string = Any(str, unicode)

_bool = Any(bool, unicode)

_non_empty_string = All(_string, Length(min=1))

_parameter_value = _string

_plugin_basic = {
    Required('name'): _non_empty_string,
    Required('active'): bool,
    Required('parameters'): [parameter_basic],
}

_plugin_full = {
    Required('name'): _non_empty_string,
    Required('active'): bool,
    Required('info'): _string,
    Required('synopsis'): _string,
    Required('warn'): _string,
    Required('citation'): [citation],
    Required('id'): _non_empty_string,
    Required('parameters'): [parameter_full],
}

server_configuration_schema = Schema({
    Required("data_location"): {
        Required("default"): _non_empty_string,
    },
    Required("process_list_location"): {
        Required("default"): _non_empty_string,
    },
    Required("output_location"): {
        Required("default"): _non_empty_string,
    },
    Required("job_runners"): {
        Extra: {
            Required("module"): _non_empty_string,
            Required("class"): _non_empty_string,
            Required("parameters"): dict,
        }
    }
})

filename_listing_schema = Schema({
    Required('path'): _non_empty_string,
    Required('files'): [_non_empty_string],
})

process_list_list_filename_schema = Schema({
    Required('filename'): _non_empty_string,
    Required('plugins'): [_plugin_full],
})

process_list_update_schema = Schema({
    Required('plugins'): [_plugin_basic],
})

process_list_delete_schema = Schema({
    Required('filename'): _non_empty_string,
})

jobs_queue_info_schema = Schema({
    Required('queue'): _non_empty_string,
    Required('job'): {
        Required('id'): _non_empty_string,
        Required('running'): bool,
        Required('successful'): bool,
        Required('status'): _non_empty_string,
        Required('output_dataset'): Any(None, _non_empty_string),
    },
})
