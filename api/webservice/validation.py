from voluptuous import Schema, Required, All, Any, Length, Extra

_string = Any(str, unicode)

_bool = Any(bool, unicode)

_non_empty_string = All(_string, Length(min=1))

_parameter_value = _string

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

