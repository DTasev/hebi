from voluptuous import Schema, Required, Any

from webservice.apps.common.validation import any_non_empty_string

jobs_queue_info_schema = Schema({
    Required('queue'): any_non_empty_string,
    Required('job'): {
        Required('id'): any_non_empty_string,
        Required('running'): bool,
        Required('successful'): bool,
        Required('status'): any_non_empty_string,
        Required('output_dataset'): Any(None, any_non_empty_string),
    },
})
