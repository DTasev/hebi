import pkgutil
import sys

import savu.plugins.utils as pu


def populate_plugins():
    """
    Loads plugins from plugin paths.

    Almost identical to the function in scripts.config_generator
    """

    def _add_module(loader, module_name):
        if module_name not in sys.modules:
            try:
                loader.find_module(module_name).load_module(module_name)
            except Exception:
                pass

    # load all the plugins
    plugins_path = pu.get_plugins_paths()
    savu_path = plugins_path[-1].split('savu')[0]
    savu_plugins = plugins_path[-1:]
    local_plugins = plugins_path[0:-1] + [savu_path + 'plugins_examples']

    # load local plugins
    for loader, module_name, is_pkg in pkgutil.walk_packages(local_plugins):
        _add_module(loader, module_name)

    # load savu plugins
    for loader, module_name, is_pkg in pkgutil.walk_packages(savu_plugins):
        if module_name.split('savu.plugins')[0] == '':
            _add_module(loader, module_name)
