import os

import savu.plugins.utils as pu
from savu.data.plugin_list import CitationInformation
from scripts.config_generator.content import Content

from webservice.apps.process_list import const


def find_files_recursive(path, pred):
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        for fn in filenames:
            ffn = os.path.join(dirpath, fn)
            if pred(ffn):
                yield ffn


def stringify_parameter_value(value):
    """
    See display_formatter.py
    """
    return str(value).replace("'", "")


def plugin_to_dict(name, p):
    """
    Returns a dictionary representation of a plugin in a given state.
    """
    parameters = []
    for param_name in p.parameters.keys():
        parameters.append({
            'name': param_name,
            'value': stringify_parameter_value(p.parameters[param_name]),
            'type': p.parameters_types[param_name].__name__,
            'description': p.parameters_desc[param_name],
            'is_user': param_name in p.parameters_user,
            'is_hidden': param_name in p.parameters_hide,
        })

    cite = p.get_citation_information()
    # We want a list, even if it just a single or no citation
    if not cite:
        cite = []
    elif isinstance(cite, CitationInformation):
        cite = [cite]

    return {
        'name': name,
        'info': p.docstring_info.get('info'),
        'synopsis': p.docstring_info.get('synopsis'),
        'warn': p.docstring_info.get('warn'),
        'citation': [citation_information_to_dict(c) for c in cite],
        'parameters': parameters,
    }


def plugin_list_entry_to_dict(p):
    # Get plugin details
    pl = pu.plugins[p['name']]()
    pl._populate_default_parameters()
    data = plugin_to_dict(p['name'], pl)

    # Format parameters
    parameters = []
    for pn in p['data'].keys():
        parameters.append({
            'name': pn,
            'value': stringify_parameter_value(p['data'][pn]),
            'description': p['desc'][pn],
            'is_user': pn in p['user'],
            'is_hidden': pn in p['hide'],
        })

    data.update({
        'parameters': parameters,
        'id': p['id'],
        'active': bool(p['active']),  # Convert from numpy bool
    })

    return data


def create_process_list_from_user_data(data):
    """
    Creates a process list from user supplied data.
    """
    process_list = Content()

    # For each plugin
    for i, pl in enumerate(data['plugins']):
        pos = str(i + 1)

        # Add plugin
        process_list.add(pl['name'], pos)

        # Set plugin enable state
        process_list.on_and_off(
            pos,
            const.PLUGIN_ENABLED if pl['active'] else const.PLUGIN_DISABLED)

        # Set parameter values
        for param in pl['parameters']:
            process_list.modify(pos, param['name'], param['value'])

    return process_list


def citation_information_to_dict(ci):
    """
    Return a dictrionary representation of citation information.
    """
    return {
        'description': ci.description,
        'doi': ci.doi,
        'endnote': ci.endnote,
        'bibtex': ci.bibtex
    }
