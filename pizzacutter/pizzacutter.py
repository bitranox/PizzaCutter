# STDLIB
import logging
import os
import pprint
import shutil
from typing import List, Optional, Union, BinaryIO

# OWN
import pathlib3x as pathlib  # type: ignore

try:
    from .sub import get_config
    from .sub import helpers
    from .sub import import_module
    from .sub.pizzacutter_config import PizzaCutterConfigBase
    # import of project_conf is only to get type hints in the ide, it will be re-imported
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    # imports for doctest
    from sub import get_config  # type: ignore  # pragma: no cover
    from sub import helpers  # type: ignore  # pragma: no cover
    from sub import import_module  # type: ignore  # pragma: no cover
    from sub.pizzacutter_config import PizzaCutterConfigBase  # type: ignore  # pragma: no cover

logger = logging.getLogger()


class PizzaCutter(object):
    """ Builds or rebuilds a project """

    def __init__(self,
                 # the path to the PizzaCutter conf File
                 path_conf_file: pathlib.Path,
                 # the path to the Template Folder - can be set by the conf File to the Directory the conf file sits - can be overridden by untrusted conf_file
                 path_template_folder: Optional[pathlib.Path] = None,
                 # the target path of the Project Folder - this should be the current Directory - can be overridden by conf_file
                 path_project_folder: Optional[pathlib.Path] = None,
                 # dry run - test only, report overwrites, files outside project directory, unset patterns, unused patterns from conf file
                 # only made the easy tests now - for full test of replacements we would need to install into a temp directory
                 dry_run: Optional[bool] = None,
                 # allow overwrite in the target Project, can be overridden by conf_file
                 allow_overwrite: Optional[bool] = None,
                 # allow to write files outside of the target Project Folder, can be overridden by conf_file
                 allow_outside_write: Optional[bool] = None,
                 quiet: Optional[bool] = None
                 ):

        self.conf = get_config.PizzaCutterGetConfig(pizza_cutter_path_conf_file=path_conf_file,
                                                    pizza_cutter_path_template_folder=path_template_folder,
                                                    pizza_cutter_path_target_folder=path_project_folder).conf

        if path_template_folder is None:
            self.path_template_folder = self.conf.pizza_cutter_path_template_folder
        else:
            self.path_template_folder = path_template_folder

        if path_project_folder is None:
            self.path_project_folder = self.conf.pizza_cutter_path_project_folder
        else:
            self.path_project_folder = path_project_folder

        if allow_overwrite is None:
            self.allow_overwrite = self.conf.pizza_cutter_allow_overwrite
        else:
            self.allow_overwrite = allow_overwrite

        if allow_outside_write is None:
            self.allow_outside_write = self.conf.pizza_cutter_allow_outside_write
        else:
            self.allow_outside_write = allow_outside_write

        if dry_run is None:
            self.dry_run = self.conf.pizza_cutter_dry_run
        else:
            self.dry_run = dry_run

        if quiet is None:
            self.quiet = self.conf.pizza_cutter_quiet
        else:
            self.quiet = quiet

        self.file_stack: List[pathlib.Path] = list()
        self.pattern_stack: List[str] = list()

    def build(self) -> None:
        self.conf.pizza_cutter_hook_before_build()
        self.resolve_str_patterns()
        self.copy_files_from_template_to_project()
        self.replace_patterns_in_files()
        self.log_unfilled_patterns()
        self.conf.pizza_cutter_hook_after_build()

    def replace_patterns_in_files(self) -> None:

        path_source_objects = self.get_path_template_objects()

        for path_source_object in path_source_objects:
            s_path_source_object_resolved = str(path_source_object)

            path_target_object = self.get_path_target_object(path_source_object=path_source_object)

            if self.do_not_copy(s_path_source_object_resolved):
                continue

            if self.skip_write_outside_project_folder(path_target_object, quiet=True):
                continue

            if path_target_object.is_file():
                # TODO: add to PathlibX append_suffix new_path = path.parent / (path.name + '.suffix')
                path_target_patterns_replaced = path_target_object.parent / (path_target_object.name + '.PizzaCutter_Temp')
                with open(str(path_target_patterns_replaced), 'wb') as f_target:
                    self.replace_patterns_in_file(path_target_object, f_target)
                path_target_object.unlink()
                path_target_patterns_replaced.rename(path_target_object)

    def replace_patterns_in_file(self, path_source_file: pathlib.Path, f_target: BinaryIO) -> None:
        """
        replace all the patterns in the source file
        it is already prepared for the function that You can include the content of other files into one file -
        we dont know if we will ever finish that idea, because we just can make the replacement in the config file,
        as long as there are no other string replacements in that included file.
        """

        # this is in preparation for the function if we can include the content of files into other files
        if path_source_file in self.file_stack:
            raise RecursionError('Recursion on path includes : \n {}'.format(pprint.pformat(self.file_stack)))
        self.file_stack.append(path_source_file)

        # this is in preparation for the function if we can include the content of files into other files
        # because on included files you need to make all replacements before

        with open(str(path_source_file), 'rb') as f_source:
            source_line = f_source.readline()
            while source_line:
                self.replace_patterns_in_source_line_and_write_to_target_file(path_source_file, source_line, f_target)
                source_line = f_source.readline()

        self.file_stack.pop()

    def replace_patterns_in_source_line_and_write_to_target_file(self, path_source_file: pathlib.Path, source_line: bytes, f_target: BinaryIO) -> None:
        if b'{{' in source_line:
            source_line = self.replace_str_patterns_in_line(source_line)
            source_line = self.replace_pathlib_patterns_in_line(path_source_file, source_line, f_target)
            source_line = self.replace_option_patterns_in_line(source_line)
        f_target.write(source_line)

    def replace_pathlib_patterns_in_line(self, path_source_file: pathlib.Path, source_line: bytes, f_target: BinaryIO) -> bytes:
        # not implemented now - You can solve it in the config file just to read the files there
        # a pathlib pattern is replaced with the str() of the pathlib replacement
        for pattern in self.conf.pizza_cutter_patterns.keys():
            replacement = self.conf.pizza_cutter_patterns[pattern]
            if not isinstance(replacement, str):
                replacement = str(replacement)
                source_line = source_line.replace(pattern.encode('utf-8'), replacement.encode('utf-8'))
        return source_line

    def replace_str_patterns_in_line(self, source_line: bytes) -> bytes:
        """
        replaces the patterns in the line
        >>> # Setup
        >>> logger=logging.getLogger()
        >>> logging.basicConfig()
        >>> logger.level=logging.DEBUG

        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_folder=path_template_folder, \
                                       path_project_folder=path_project_folder, \
                                       dry_run= True)

        >>> pizza_cutter.conf.pizza_cutter_patterns['pizzacutter'] = 'doctest'
        >>> pizza_cutter.replace_str_patterns_in_line(b'this is a test in pizzacutter')
        b'this is a test in doctest'

        """

        for pattern in self.conf.pizza_cutter_patterns.keys():
            replacement = self.conf.pizza_cutter_patterns[pattern]
            if isinstance(replacement, str):
                source_line = source_line.replace(pattern.encode('utf-8'), replacement.encode('utf-8'))

        return source_line

    def resolve_str_patterns(self) -> None:
        """
        if You read another template file into a string replacement, we need to recursively also replace those patterns.
        this works only for string replacements. If a string pattern contains pathlib.Path Patterns in the replacement string,
        those will be converted to String.

        >>> # Setup
        >>> logger=logging.getLogger()
        >>> logging.basicConfig()
        >>> logger.level=logging.DEBUG

        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_folder=path_template_folder, \
                                       path_project_folder=path_project_folder, \
                                       dry_run= True)

        >>> # Test
        >>> pizza_cutter.conf.pizza_cutter_patterns = dict()
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test1}}'] = 'test1 {{TestPizzaCutter.test2}} {{TestPizzaCutter.test3}}'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test2}}'] = 'test2 {{TestPizzaCutter.test3}} {{TestPizzaCutter.test4}}'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test3}}'] = 'test3'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test4}}'] = 'test4'
        >>> pizza_cutter.resolve_str_patterns()
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test1}}']
        'test1 test2 test3 test4 test3'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test2}}']
        'test2 test3 test4'

        >>> # Test recursion
        >>> pizza_cutter.conf.pizza_cutter_patterns = dict()
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test1}}'] = 'test1 {{TestPizzaCutter.test2}} {{TestPizzaCutter.test3}}'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test2}}'] = 'test2 {{TestPizzaCutter.test3}} {{TestPizzaCutter.test4}}'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test3}}'] = 'test3 {{TestPizzaCutter.test1}}'
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.test4}}'] = 'test4'
        >>> pizza_cutter.resolve_str_patterns()
        Traceback (most recent call last):
            ...
        RecursionError: "{{TestPizzaCutter.test3}}" refers back to "{{TestPizzaCutter.test1}}"
        <BLANKLINE>
        Stack:
        ['{{TestPizzaCutter.test1}}', '{{TestPizzaCutter.test2}}', '{{TestPizzaCutter.test3}}']


        """
        for pattern in self.conf.pizza_cutter_patterns.keys():
            replacement = self.conf.pizza_cutter_patterns[pattern]
            if isinstance(replacement, str):
                self.resolve_str_patterns_recursive(pattern)

    def resolve_str_patterns_recursive(self, pattern: str) -> str:
        if pattern in self.pattern_stack:
            raise RecursionError('"{last_entry}" refers back to "{pattern}"\n\nStack:\n{stack}'.format(stack=pprint.pformat(self.pattern_stack),
                                                                                                       last_entry=self.pattern_stack[-1],
                                                                                                       pattern=pattern))
        self.pattern_stack.append(pattern)

        replacement = str(self.conf.pizza_cutter_patterns[pattern])
        for sub_pattern in self.conf.pizza_cutter_patterns.keys():
            if sub_pattern in replacement:
                sub_replacement = self.resolve_str_patterns_recursive(sub_pattern)
                replacement = replacement.replace(sub_pattern, sub_replacement)
                self.conf.pizza_cutter_patterns[pattern] = replacement

        self.pattern_stack.pop()

        return replacement

    def replace_option_patterns_in_line(self, source_line: bytes) -> bytes:
        """

        >>> # Setup
        >>> logger=logging.getLogger()
        >>> logging.basicConfig()
        >>> logger.level=logging.DEBUG

        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_folder=path_template_folder, \
                                       path_project_folder=path_project_folder, \
                                       dry_run= True)

        >>> # test line not empty, without option 'delete_line_if_empty' set :
        >>> pizza_cutter.conf.pizza_cutter_patterns['pizzacutter'] = 'doctest'
        >>> source_line = pizza_cutter.replace_str_patterns_in_line(b'pizzacutter\\n')
        >>> assert pizza_cutter.replace_option_patterns_in_line(source_line) == b'doctest\\n'

        >>> # test line empty, without option 'delete_line_if_empty' set :
        >>> pizza_cutter.conf.pizza_cutter_patterns['pizzacutter'] = ''
        >>> source_line = pizza_cutter.replace_str_patterns_in_line(b'pizzacutter\\n')
        >>> assert pizza_cutter.replace_option_patterns_in_line(source_line) == b'\\n'

        >>> # test line not empty, with option 'delete_line_if_empty' set :
        >>> pizza_cutter.conf.pizza_cutter_patterns['pizzacutter'] = 'doctest'
        >>> source_line = pizza_cutter.replace_str_patterns_in_line(b'pizzacutter{{TestPizzaCutter.option.delete_line_if_empty}}\\n')
        >>> assert pizza_cutter.replace_option_patterns_in_line(source_line) == b'doctest\\n'

        >>> # test line empty, with option 'delete_line_if_empty' set :
        >>> pizza_cutter.conf.pizza_cutter_patterns['pizzacutter'] = ''
        >>> source_line = pizza_cutter.replace_str_patterns_in_line(b'pizzacutter{{TestPizzaCutter.option.delete_line_if_empty}}\\n')
        >>> assert pizza_cutter.replace_option_patterns_in_line(source_line) == b''


        """
        for option in self.conf.pizza_cutter_options.keys():
            pattern = self.conf.pizza_cutter_options[option]
            pattern_bytes = pattern.encode('utf-8')
            if pattern_bytes in source_line:
                source_line = source_line.replace(pattern_bytes, b'')
                if option == 'delete_line_if_empty' and source_line.strip() == b'':
                    source_line = b''
        return source_line

    def copy_files_from_template_to_project(self) -> None:
        """
        Builds or rebuilds a project

        >>> # Setup
        >>> logger=logging.getLogger()
        >>> logging.basicConfig()
        >>> logger.level=logging.DEBUG

        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_expected_folder = path_test_dir / 'pizzacutter_test_project_01_expected'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)
        >>> shutil.rmtree(path_project_folder, ignore_errors=True)

        >>> # Test Create Files
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_folder=path_template_folder, \
                                       path_project_folder=path_project_folder, \
                                       dry_run= False)
        >>> pizza_cutter.copy_files_from_template_to_project()
        >>> assert len(list(path_expected_folder.glob('./**/*'))) == len(list(path_project_folder.glob('./**/*')))

        >>> # Test Update Files
        >>> pizza_cutter.copy_files_from_template_to_project()
        >>> assert len(list(path_expected_folder.glob('./**/*'))) == len(list(path_project_folder.glob('./**/*')))

        >>> # Teardown
        >>> shutil.rmtree(path_project_folder)


        """
        path_source_objects = self.get_path_template_objects()

        for path_source_object in path_source_objects:
            s_path_source_object = str(path_source_object)

            path_target_object_resolved = self.get_path_target_object(path_source_object=path_source_object)

            if self.do_not_copy(s_path_source_object):
                continue

            if self.skip_write_outside_project_folder(path_target_object_resolved):
                continue

            if self.skip_overwrite(s_path_source_object, path_target_object_resolved):
                continue

            if self.dry_run:
                continue

            if path_source_object.is_dir():
                helpers.create_target_directory(path_target_object_resolved)
            else:
                helpers.create_target_directory(path_target_object_resolved.parent)
                # because sometime we receive "permission denied" when overwriting the file (weired)
                path_target_object_resolved.unlink(missing_ok=True)
                shutil.copy2(str(path_source_object), str(path_target_object_resolved))

    def do_not_copy(self, file_object_name: str) -> bool:
        """ Check if the pattern for option 'object_no_copy' in file_object_name """
        if self.conf.pizza_cutter_options['object_no_copy'] in file_object_name:
            return True
        else:
            return False

    def skip_write_outside_project_folder(self, path_target_object: pathlib.Path, quiet: Optional[bool] = None) -> bool:
        """ Check if skipped because outside project folder not allowed """

        skip_outside_write = False

        if quiet is None:
            quiet = self.quiet

        if helpers.path_startswith(path_target_object, self.path_project_folder):
            return skip_outside_write

        if self.allow_outside_write:
            if self.dry_run and not quiet:
                logger.info('object outside project directory: "{}"'.format(path_target_object))
            skip_outside_write = False
        else:
            msg = 'object outside project directory not allowed: "{}"'.format(path_target_object)
            if self.dry_run and not quiet:
                logger.info(msg)
            else:
                if not quiet:
                    logger.warning(msg)
            skip_outside_write = True

        return skip_outside_write

    def skip_overwrite(self, s_path_source_object: str, path_target_object_resolved: pathlib.Path) -> bool:
        """ check if overwrite is allowed """

        if self.conf.pizza_cutter_options['object_no_overwrite'] in s_path_source_object and path_target_object_resolved.exists():
            return True

        if path_target_object_resolved.exists():
            if self.allow_overwrite:
                if self.dry_run:
                    logger.debug('object will be overwritten: "{}"'.format(path_target_object_resolved))
                return False
            else:
                if self.dry_run:
                    logger.debug('object overwrite skipped, because allow_overwrite = False: "{}"'.format(path_target_object_resolved))
                return True
        else:
            return False

    def log_unfilled_patterns(self) -> None:

        path_source_objects = self.get_path_template_objects()

        for path_source_object in path_source_objects:
            s_path_source_object_resolved = str(path_source_object)

            path_target_object = self.get_path_target_object(path_source_object=path_source_object)

            if self.do_not_copy(s_path_source_object_resolved):
                continue

            if self.skip_write_outside_project_folder(path_target_object, quiet=True):
                continue

            self.log_unfilled_pattern_in_object_name(path_target_object)
            self.log_unfilled_pattern_in_object(path_target_object)

    def log_unfilled_pattern_in_object_name(self, path_object: pathlib.Path) -> None:
        object_path_name = str(path_object)
        for prefix in self.conf.pizzacutter_pattern_prefixes:
            if prefix in object_path_name:
                full_prefix = prefix + object_path_name.split(prefix, 1)[1].split('}}', 1)[0] + '}}'
                logger.warning('unfilled Pattern "{full_prefix}" in Filename "{object_path_name}"'.format(full_prefix=full_prefix,
                                                                                                          object_path_name=object_path_name))

    def log_unfilled_pattern_in_object(self, path_object: pathlib.Path) -> None:
        """
        find unfilled patterns in the file contents.
        we search for bytes, because we dont know the encoding of the file
        """
        if path_object.is_file():
            content_bytes = path_object.read_bytes()
            for prefix in self.conf.pizzacutter_pattern_prefixes:
                prefix_bytes = prefix.encode('utf-8')
                if prefix_bytes in content_bytes:
                    full_prefix_bytes = prefix_bytes + content_bytes.split(prefix_bytes, 1)[1].split(b'}}', 1)[0] + b'}}'
                    full_prefix = full_prefix_bytes.decode('utf-8')
                    logger.warning('unfilled Pattern "{full_prefix}" in File "{path_object}"'.format(full_prefix=full_prefix, path_object=path_object))

    def path_remove_cutter_option_patterns(self, path_source_file: pathlib.Path) -> pathlib.Path:
        """
        removes option patterns from the filename - those are already checked and considered earlier

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> # test ok
        >>> test_file = path_template_folder/ 'test.txt{{TestPizzaCutter.option.no_copy}}'
        >>> pizza_cutter.path_remove_cutter_option_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_template_01/test.txt')

        >>> # directory only option patterns Fails
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.option.no_copy}}/test.txt{{TestPizzaCutter.option.no_copy}}'
        >>> pizza_cutter.path_remove_cutter_option_patterns(test_file)
        Traceback (most recent call last):
            ...
        RuntimeError: No part of the path ...

        >>> # File only option patterns Fails
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.option.no_copy}}.test/{{TestPizzaCutter.option.no_copy}}'
        >>> pizza_cutter.path_remove_cutter_option_patterns(test_file)
        Traceback (most recent call last):
            ...
        RuntimeError: No part of the path ...

        """
        source_file_parts = path_source_file.parts
        result_file_parts = list()
        for source_file_part in source_file_parts:
            for option_pattern in self.conf.pizza_cutter_options.values():
                source_file_part = source_file_part.replace(option_pattern, '')
            if not source_file_part:
                raise RuntimeError('No part of the path must consist ONLY of option patterns: "{}"'.format(path_source_file))
            result_file_parts.append(source_file_part)
        result_path_source_file = pathlib.Path(*result_file_parts)
        return result_path_source_file

    def get_path_target_object(self, path_source_object: pathlib.Path) -> pathlib.Path:
        path_source_object = self.path_replace_string_patterns(path_source_object)
        path_source_object = self.path_remove_cutter_option_patterns(path_source_object)
        path_target_object_resolved = self.path_replace_pathlib_patterns(path_source_object)
        return path_target_object_resolved

    def path_replace_string_patterns(self, path_source_object_resolved: pathlib.Path) -> pathlib.Path:
        """
        replaces string patterns in the filename

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> # test no replacements
        >>> test_file = path_template_folder/ 'test.txt'
        >>> pizza_cutter.path_replace_string_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_template_01/test.txt')

        >>> # test with replacement
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.doctest}}'] = 'doctest'
        >>> test_file = path_template_folder/ 'test_{{TestPizzaCutter.doctest}}.txt'
        >>> pizza_cutter.path_replace_string_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_template_01/test_doctest.txt')


        """
        source_file_parts = path_source_object_resolved.parts
        result_file_parts = list()
        for source_file_part in source_file_parts:
            for pattern in self.conf.pizza_cutter_patterns.keys():
                replacement = self.conf.pizza_cutter_patterns[pattern]
                if isinstance(replacement, str):
                    source_file_part = source_file_part.replace(pattern, replacement)
            result_file_parts.append(source_file_part)
        result_path_source_file = pathlib.Path(*result_file_parts)
        return result_path_source_file

    def path_replace_pathlib_patterns(self, path_source_object: pathlib.Path) -> pathlib.Path:
        """
        Returns the resolved Target Path

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> # test absolute replacement + relative replacement
        >>> import platform
        >>> if platform.system().lower() == 'windows':
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.Path('c:/test/doctest_absolute')
        ... else:
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.Path('/test/doctest_absolute')
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.Path('./doctest')
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.path.doctest.absolute}}/{{TestPizzaCutter.path.doctest.relative}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../doctest_absolute/doctest/test.txt')

        >>> # test no replacements
        >>> test_file = path_template_folder/ 'test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_project_01/test.txt')

        >>> # test relative replacements
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.PurePosixPath('./doctest')
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.path.doctest.relative}}/{{TestPizzaCutter.path.doctest.relative}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_project_01/doctest/doctest/test.txt')

        >>> # test relative replacement + absolute replacement
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.PurePosixPath('/test/doctest_absolute')
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.PurePosixPath('./doctest')
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.path.doctest.relative}}/{{TestPizzaCutter.path.doctest.absolute}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../doctest_absolute/test.txt')

        >>> # test absolute replacement + absolute replacement (last "wins")
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute1}}'] = pathlib.PurePosixPath('/test/doctest_absolute1')
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute2}}'] = pathlib.PurePosixPath('/test/doctest_absolute2')
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.path.doctest.absolute1}}/{{TestPizzaCutter.path.doctest.absolute2}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../doctest_absolute2/test.txt')

        >>> # test path replacement not complete part of a path (name is also a complete part !!!)
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.PurePosixPath('./doctest')
        >>> test_file = path_template_folder/ '{{TestPizzaCutter.path.doctest.relative}}/{{TestPizzaCutter.path.doctest.relative}}.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        Traceback (most recent call last):
            ...
        RuntimeError: ... can only be one complete part of a path : ...{{...doctest.relative}}.txt", Pattern: {{TestPizzaCutter.path.doctest.relative}}

        """

        source_object_parts = reversed(path_source_object.parts)
        target_parts = list()
        absolute_path_found = False
        for source_object_part in source_object_parts:
            target_object_part: Union[str, pathlib.Path] = source_object_part
            for pattern in self.conf.pizza_cutter_patterns.keys():
                replacement = self.conf.pizza_cutter_patterns[pattern]
                # we need this, because pathlib3x.Path is NOT instance of pathlib.Path,
                # but the User might use pathlib in his config File !
                if isinstance(replacement, str):
                    continue
                if pattern in source_object_part:
                    if source_object_part != pattern:
                        raise RuntimeError(
                            'pathlib.Path patterns can only be one complete part of a path : Path: "{path_source_file}", Pattern: {pattern}'.format(
                                path_source_file=path_source_object, pattern=pattern))
                    else:
                        target_object_part = pathlib.Path(replacement)
                        if target_object_part.is_absolute() and absolute_path_found:
                            logger.warning(
                                'the resulting path might be unexpected, You have more then one absolute pathlib.Path pattern in the path: '
                                '"{path_source_file}", Pattern: "{pattern}" points to "{replacement}"'.format(
                                    path_source_file=path_source_object, pattern=pattern, replacement=replacement))

            if not absolute_path_found:
                target_parts.append(target_object_part)
                if not isinstance(target_object_part, str) and pathlib.Path(target_object_part).is_absolute():
                    absolute_path_found = True

        target_parts = list(reversed(target_parts))
        path_target_path = pathlib.Path(*target_parts).resolve()

        if absolute_path_found:
            logger.warning('the resulting path of a template file might be unexpected, You have an absolute pathlib.Path pattern in the path: '
                           '"{path_source_file}" points to "{path_target_path}"'.format(path_source_file=path_source_object,
                                                                                        path_target_path=path_target_path))
        else:
            path_target_path = helpers.replace_source_dir_path_with_target_dir_path(pathlib_path=path_target_path,
                                                                                    path_source_dir=self.path_template_folder,
                                                                                    path_target_dir=self.path_project_folder)
        return path_target_path

    def get_path_template_subdirs_with_pattern(self) -> List[pathlib.Path]:
        """
        get the template sub directories with a valid pattern in it - all other directories are considered not to be part of the template

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'

        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> # TEST
        >>> pizza_cutter.get_path_template_subdirs_with_pattern()
        [...Path('.../pizzacutter_test_template_01/{{TestPizzaCutter.project_dir}}')...]

        """

        template_subdirs_with_pattern: List[pathlib.Path] = list()
        path_template_dir_subdirs = list(self.path_template_folder.glob('*/'))
        for path_template_subdir in path_template_dir_subdirs:
            for pattern in self.conf.pizza_cutter_patterns.keys():
                if pattern in path_template_subdir.name:
                    template_subdirs_with_pattern.append(path_template_subdir)
        return template_subdirs_with_pattern

    def get_path_template_objects(self) -> List[pathlib.Path]:
        """
        get all the files in the template sub directories with a valid pattern

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_folder = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_folder / 'PizzaCutterTestConfig_01.py'
        >>> path_project_folder = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_folder, path_project_folder)

        >>> savedir = pathlib.Path.cwd().resolve()
        >>> os.chdir(path_template_folder)

        >>> # TEST
        >>> pizza_cutter.get_path_template_objects()
        [...Path('.../tests/pizzacutter_test_template_01/{{TestPizzaCutter.project_dir}}'), ...]

        >>> # Teardown
        >>> os.chdir(str(savedir))

        """
        path_template_files: List[pathlib.Path] = list()
        for path_directory in self.get_path_template_subdirs_with_pattern():
            path_template_files = path_template_files + list(path_directory.glob('**/*')) + list(path_directory.glob('**/'))
        path_template_files = sorted(list(set(path_template_files)))
        return path_template_files


def build(path_conf_file: pathlib.Path,
          path_template_folder: Optional[pathlib.Path] = None,
          path_target_folder: Optional[pathlib.Path] = None,
          dry_run: Optional[bool] = None,
          allow_overwrite: Optional[bool] = None,
          allow_outside_write: Optional[bool] = None,
          quiet: Optional[bool] = None) -> None:

    pizza_cutter = PizzaCutter(path_conf_file=path_conf_file,
                               path_template_folder=path_template_folder,
                               path_project_folder=path_target_folder,
                               dry_run=dry_run,
                               allow_overwrite=allow_overwrite,
                               allow_outside_write=allow_outside_write,
                               quiet=quiet)

    pizza_cutter.build()


if __name__ == '__main__':
    print('this is a library only, the executable is named pizzacutter_cli.py')
