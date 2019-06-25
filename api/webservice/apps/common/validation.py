from voluptuous import Required, Optional, All, Any, Length

any_string = Any(str, unicode)

any_bool = Any(bool, unicode)

any_non_empty_string = All(any_string, Length(min=1))

any_parameter_value = any_string

citation = {
    Required('bibtex'): any_string,
    Required('description'): any_string,
    Required('endnote'): any_string,
    Required('doi'): any_string,
}

parameter_basic = {
    Required('name'): any_non_empty_string,
    Required('value'): any_parameter_value,
}

parameter_full = parameter_basic.copy()
parameter_full.update({
    Required('description'): any_non_empty_string,
    Optional('type'): any_non_empty_string,
    Required('is_user'): bool,
    Required('is_hidden'): bool,
    Required('value'): any_non_empty_string
})
