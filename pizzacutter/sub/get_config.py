# STDLIB
import pathlib3x as pathlib
from typing import Optional

# PROJ
try:
    from . import pizzacutter_config
    from . import import_module
except (ImportError, ModuleNotFoundError, ValueError):  # pragma: no cover
    import pizzacutter_config           # type: ignore  # pragma: no cover
    import import_module                # type: ignore  # pragma: no cover


class PizzaCutterGetConfig(object):
    """
    >>> path_test_dir = pathlib.Path(__file__).parent.parent.parent / 'tests'
    >>> pizza_cutter_path_conf_file = path_test_dir / 'pizzacutter_test_template_01/PizzaCutterTestConfig_01.py'
    >>> pizza_cutter_conf = PizzaCutterGetConfig(pizza_cutter_path_conf_file = pizza_cutter_path_conf_file)
    >>> assert pizza_cutter_conf.conf.project_dir == 'pizzacutter_test_project'

    """
    def __init__(self,
                 # the path to the PizzaCutter conf File
                 pizza_cutter_path_conf_file: pathlib.Path,
                 # the path to the Template Folder - can be set by the conf File to the Directory the conf file sits - can be overridden by conf file
                 pizza_cutter_path_template_dir: Optional[pathlib.Path] = None,
                 # the target path of the Project Folder - this should be the current Directory - can be overridden by conf file
                 pizza_cutter_path_target_dir: Optional[pathlib.Path] = None):

        # make sure it is a pathlib3x instance
        pizza_cutter_path_conf_file = pathlib.Path(pizza_cutter_path_conf_file)
        self.conf = pizzacutter_config.PizzaCutterConfigBase()
        reloaded_mod_conf = import_module.import_module_from_file(module_fullpath=pizza_cutter_path_conf_file, reload=True)
        self.conf = reloaded_mod_conf.PizzaCutterConfig(pizza_cutter_path_conf_file=pizza_cutter_path_conf_file,
                                                        pizza_cutter_path_template_dir=pizza_cutter_path_template_dir,
                                                        pizza_cutter_path_target_dir=pizza_cutter_path_target_dir)
