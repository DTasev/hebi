from voluptuous import Schema, Required

from webservice.apps.common.validation import any_non_empty_string
from webservice.apps.job import PROCESS_LIST_FILE, PROCESS_LIST_NAME
from webservice.apps.job.postparams import DATA_DIR

job_run_schema = Schema({
    Required(PROCESS_LIST_FILE): any_non_empty_string,
    Required(PROCESS_LIST_NAME): any_non_empty_string,
    Required(DATA_DIR): any_non_empty_string
})
