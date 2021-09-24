# stdlib
import pathlib3x as pathlib
from typing import Dict, Optional, Union


# we need this construction to be able to override path_conf_file, path_template_dir, path_target_dir by commandline
# and to re-evaluate depending values
class PizzaCutterConfigBase(object):
    def __init__(self,
                 # the path to the actual config File
                 pizza_cutter_path_conf_file: Optional[pathlib.Path] = None,
                 # the default for the template Folder is the actual directory of the given config File
                 pizza_cutter_path_template_dir: Optional[pathlib.Path] = None,
                 # the project Folder is the current directory
                 pizza_cutter_path_target_dir: Optional[pathlib.Path] = None):
        """
        The Base Class for the Pizza Cutter Configuration

        >>> # Test Config File not found
        >>> config = PizzaCutterConfigBase(pizza_cutter_path_conf_file=pathlib.Path('not_existing_conf_file'))
        Traceback (most recent call last):
        ...
        FileNotFoundError: PizzaCutter config file "not_existing_conf_file" does not exist

        >>> # Test Config File not found
        >>> config = PizzaCutterConfigBase(pizza_cutter_path_template_dir=pathlib.Path('not_existing_template_directory'))
        Traceback (most recent call last):
        ...
        NotADirectoryError: Template Directory "not_existing_template_directory" must be an existing Directory

        """

        if pizza_cutter_path_conf_file is None:
            pizza_cutter_path_conf_file = pathlib.Path(__file__).resolve()
        else:
            if not pizza_cutter_path_conf_file.is_file():
                raise FileNotFoundError(f'PizzaCutter config file "{pizza_cutter_path_conf_file}" does not exist')
            # make sure it is a pathlib3x object
            pizza_cutter_path_conf_file = pathlib.Path(pizza_cutter_path_conf_file)
            pizza_cutter_path_conf_file = pizza_cutter_path_conf_file.resolve()

        if pizza_cutter_path_template_dir is None:
            pizza_cutter_path_template_dir = pizza_cutter_path_conf_file.resolve().parent
        else:
            if not pizza_cutter_path_template_dir.is_dir():
                raise NotADirectoryError(f'Template Directory "{pizza_cutter_path_template_dir}" must be an existing Directory')
            # make sure it is a pathlib3x object
            pizza_cutter_path_template_dir = pathlib.Path(pizza_cutter_path_template_dir)
            pizza_cutter_path_template_dir = pizza_cutter_path_template_dir.resolve()

        if pizza_cutter_path_target_dir is None:
            pizza_cutter_path_target_dir = pathlib.Path.cwd().resolve()
        else:
            # make sure it is a pathlib3x object
            pizza_cutter_path_target_dir = pathlib.Path(pizza_cutter_path_target_dir)

        self.pizza_cutter_path_conf_file = pizza_cutter_path_conf_file
        self.pizza_cutter_path_template_dir = pizza_cutter_path_template_dir
        self.pizza_cutter_path_target_dir = pizza_cutter_path_target_dir
        self.pizza_cutter_options: Dict[str, str] = dict()

        # the settings from the CLI can only be overwritten by configuration files
        self.pizza_cutter_allow_overwrite = False
        self.pizza_cutter_allow_outside_write = False
        self.pizza_cutter_dry_run = False
        self.pizza_cutter_quiet = False

        # for patterns to look out after all replacements, in order to find unfilled patterns
        self.pizzacutter_pattern_prefixes = ['{{PizzaCutter', '{{cookiecutter', '{{pizzacutter', '{{Pizzacutter']

        # ######################################################################################################################################################
        # replacement patterns
        # ######################################################################################################################################################

        # replacement patterns can be string, or pathlib.Path Objects - the pathlib Objects can be absolute or relative
        # if You chain such pathlib Objects in template files or directories,, the final destination of the file might be not were You expected.
        # since You might pass relative or absolute paths to the PizzaCutter CLI Application, You should be careful
        # about the resulting paths, especially if You pass absolute paths.

        # beware of differences in Linux and Windows : on Windows pathlib.Path('/test') is relative, on Linux it is absolute !
        # best practice is to use relative paths in the form pathlib.Path('./test')

        # with great flexibility there comes big responsibility. You should test Your Pizzacutter conf_files with absolute and relative Paths

        # for the project path, and check carefully the result. We might disallow absolute paths in the future, or only enable it with a flag,
        # not to allow dangerous Pizzacutter conf_files to overwrite system files.

        # in general, if not really needed on purpose, we would suggest to use only string replacements in directory- and filenames.
        # on the other hand, this feature can be very useful, in order t drop files to the user desktop,
        # user home, windows appdir, etc... OUTSIDE of the Project Path given

        # path replacement patterns are also valid in text files
        # in that case the pattern will be replaced with the content of that file (if found)
        # if the file is not found, or not readable, the string of the path will be filled in. (with a warning)
        # You can even include Files from outside the template Folder, or from the Project Folder itself.

        # Those replacements will be done AFTER the template Files are copied to the target Project, to make sure that even
        # replacements from the target project file work properly.

        # this can be useful for situations like:
        # /template_folder/my_special_configuration{{PizzaCutter.option.no_overwrite}}.txt                          # template for the special configuration
        # /template_folder/some_file.txt        # that file includes /project_folder/my_special_configuration.txt
        # in that case, /project_folder/some_file.txt will include /project_folder/my_special_configuration.txt correctly,
        # even if the project is just created.

        # chaining of only relative Paths :
        # {{PizzaCutter.relative_path_object1}} = pathlib.Path('test1/test2')   # relative path
        # {{PizzaCutter.relative_path_object2}} = pathlib.Path('test3/test4')   # relative path
        # .../template_directory/{{PizzaCutter.relative_path_object1}}/{{PizzaCutter.relative_path_object2}}/test.txt  will work as expected. and resolve to:
        # .../template_directory/test1/test2/test3/test4/test.txt --> .../project_directory/test1/test2/test3/test4/test.txt

        # chaining of Absolute and Relative Paths :
        # {{PizzaCutter.absolute_path_object1}} = pathlib.Path('/test1/test2')  # absolute Path
        # {{PizzaCutter.relative_path_object2}} = pathlib.Path('test3/test4')   # relative path
        # .../template_directory/{{PizzaCutter.absolute_path_object1}}/{{PizzaCutter.relative_path_object2}}/test.txt  will work as expected. and resolve to:
        # /test1/test2/test3/test4/test.txt
        # by that way You might even write configuration files into /usr/etc or similar (depending on Your rights)!

        # unexpected Result when chaining Absolute and Relative Paths in the wrong order :
        # {{PizzaCutter.relative_path_object1}} = pathlib.Path('test1/test2')   # relative Path
        # {{PizzaCutter.absolute_path_object2}} = pathlib.Path('/test3/test4')  # absolute path
        # .../template_directory/{{PizzaCutter.relative_path_object1}}/{{PizzaCutter.absolute_path_object2}}/test.txt will work unexpected and resolve to:
        # /test3/test4/test.txt
        # by that way You might even write configuration files into /usr/etc or similar (depending on Your rights)!

        # ######################################################################################################################################################

        self.pizza_cutter_patterns: Dict[str, Union[str, pathlib.Path]] = dict()
        # this is useful in scripts, to detect if cutting already happened
        # for instance bash:  if [[ "{{PizzaCutter.True}}" == "True" ]]; then ...
        self.pizza_cutter_patterns['{{PizzaCutter.True}}'] = 'True'

        # ######################################################################################################################################################
        # cutter_options
        # ######################################################################################################################################################

        # You might name Your Patterns as You like, for instance CakeCutter, LemonCutter, MelonCutter whatever ;-)
        # even the Names for the Option Flags can be configured here
        # You must not change the keys for that options, those are hardcoded
        self.pizza_cutter_options['delete_line_if_empty'] = '{{PizzaCutter.option.delete_line_if_empty}}'  # the line will be deleted if empty
        # files or directories with that marker that will not be copied to target
        # files within a directory with that marker will not be copied to target, so You dont have to mark each file seperately
        self.pizza_cutter_options['object_no_copy'] = '{{PizzaCutter.option.no_copy}}'
        # files or directories with that marker that will not overwritten on Target
        # files within a directory with that marker will not be overwritten on the target, so You dont have to mark each file seperately
        self.pizza_cutter_options['object_no_overwrite'] = '{{PizzaCutter.option.no_overwrite}}'

    # ######################################################################################################################################################
    # Hooks
    # ######################################################################################################################################################

    def pizza_cutter_hook_before_build(self) -> None:
        pass

    def pizza_cutter_hook_after_build(self) -> None:
        pass
