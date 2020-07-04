# stdlib
import pathlib3x as pathlib
from typing import Optional

try:
    from PizzaCutter.pizzacutter.sub.pizzacutter_config import PizzaCutterConfigBase    # type: ignore
except (ImportError, ModuleNotFoundError):          # pragma: no cover
    from pizzacutter import PizzaCutterConfigBase   # type: ignore # pragma: no cover


class PizzaCutterConfig(PizzaCutterConfigBase):
    def __init__(self,
                 pizza_cutter_path_conf_file: pathlib.Path = pathlib.Path(__file__).parent.resolve(),
                 pizza_cutter_path_template_dir: Optional[pathlib.Path] = None,
                 pizza_cutter_path_target_dir: Optional[pathlib.Path] = None):
        super().__init__(pizza_cutter_path_conf_file, pizza_cutter_path_template_dir, pizza_cutter_path_target_dir)

# ##############################################################################################################################################################
# PizzaCutterConfiguration
# ##############################################################################################################################################################

        self.pizza_cutter_allow_overwrite = False
        self.pizza_cutter_allow_outside_write = False
        self.pizza_cutter_allow_outside_read = False

        # redefine for doctest
        self.pizza_cutter_options['delete_line_if_empty'] = '{{TestPizzaCutter.option.delete_line_if_empty}}'  # the line will be deleted if empty
        self.pizza_cutter_options['object_no_copy'] = '{{TestPizzaCutter.option.no_copy}}'
        self.pizza_cutter_options['object_no_overwrite'] = '{{TestPizzaCutter.option.no_overwrite}}'

        # redefine for doctest
        self.pizzacutter_pattern_prefixes = ['{{PizzaCutter.', '{{cookiecutter.', '{{TestPizzaCutter']

# ##############################################################################################################################################################
# Project Configuration - single point for all configuration of the project
# ##############################################################################################################################################################
        # the name of the project, for instance for the travis repo slug
        path_test_dir = pathlib.Path(__file__).parent.parent.resolve()
        outside_target_dir = path_test_dir / 'outside_target_dir'
        self.project_dir = 'pizzacutter_test_project'
        self.pizza_cutter_patterns['{{TestPizzaCutter.project_dir}}'] = self.project_dir
        self.pizza_cutter_patterns['{{TestPizzaCutter.doctest}}'] = 'doctest'
        self.pizza_cutter_patterns['{{TestPizzaCutter.outside_target_dir}}'] = outside_target_dir
