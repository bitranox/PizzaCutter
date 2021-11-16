# STDLIB
import logging
import os
import pprint
from typing import List, Optional, Union, BinaryIO

# OWN
import pathlib3x as pathlib

try:
    from .sub import get_config
    from .sub import helpers
    from .sub.helpers import find_version_number_in_file
    from .sub import import_module
    from .sub.pizzacutter_config import PizzaCutterConfigBase
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    # imports for doctest
    from sub import get_config  # type: ignore  # pragma: no cover
    from sub import helpers  # type: ignore  # pragma: no cover
    from sub.helpers import find_version_number_in_file
    from sub import import_module  # type: ignore  # pragma: no cover
    from sub.pizzacutter_config import PizzaCutterConfigBase  # type: ignore  # pragma: no cover

logger = logging.getLogger()


class PizzaCutter(object):
    """ Builds or rebuilds a project """

    def __init__(self,
                 # the path to the PizzaCutter conf File
                 path_conf_file: pathlib.Path,
                 # the path to the Template Folder - can be set by the conf File to the Directory the conf file sits - can be overridden by untrusted conf_file
                 path_template_dir: Optional[pathlib.Path] = None,
                 # the target path of the Project Folder - this should be the current Directory - can be overridden by conf_file
                 path_target_dir: Optional[pathlib.Path] = None,
                 # dry run - test only, report overwrites, files outside project directory, unset patterns, unused patterns from conf file
                 # only made the easy tests now - for full test of replacements we would need to install into a temp directory
                 dry_run: Optional[bool] = None,
                 # allow overwrite in the target Project, can be overridden by conf_file
                 allow_overwrite: Optional[bool] = None,
                 # allow to write files outside of the target Project Folder, can be overridden by conf_file
                 allow_outside_write: Optional[bool] = None,
                 quiet: Optional[bool] = None
                 ):
        """ Init reads the config file and sets up the neccessary class properties

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent.resolve() / 'tests'
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'

        >>> # Test init, only conf file passed, quiet
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, quiet=True)

        >>> # Test init, conf file not found
        >>> pizza_cutter = PizzaCutter(path_conf_file=pathlib.Path(), quiet=True)
        Traceback (most recent call last):
        ...
        FileNotFoundError: the config file ... can not be found

        """

        if not path_conf_file.is_file():
            raise FileNotFoundError(f'the config file "{path_conf_file}" can not be found')

        self.conf = get_config.PizzaCutterGetConfig(pizza_cutter_path_conf_file=path_conf_file,
                                                    pizza_cutter_path_template_dir=path_template_dir,
                                                    pizza_cutter_path_target_dir=path_target_dir).conf

        if path_template_dir is None:
            # we call again pathlib.Path, to be sure it is pathlib3x Type
            self.path_template_dir = pathlib.Path(self.conf.pizza_cutter_path_template_dir)
        else:
            self.path_template_dir = pathlib.Path(path_template_dir)

        if path_target_dir is None:
            self.path_target_dir = pathlib.Path(self.conf.pizza_cutter_path_target_dir)
        else:
            self.path_target_dir = pathlib.Path(path_target_dir)

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
        """ builds or rebuilds the target based on the conf file and template given"""
        self.conf.pizza_cutter_hook_before_build()
        self.resolve_str_patterns()
        self.copy_files_from_template_to_project()
        self.replace_patterns_in_files()
        self.log_unfilled_patterns()
        self.conf.pizza_cutter_hook_after_build()

    def replace_patterns_in_files(self) -> None:
        """
        replaces the patterns in each file

        """

        path_source_objects = self.get_path_template_objects()

        for path_source_object in path_source_objects:

            path_target_object = self.get_path_target_object(path_source_object=path_source_object)

            if self.do_not_copy(path_source_object):
                continue

            if self.skip_write_outside_project_folder(path_target_object, quiet=True):
                continue

            if path_target_object.is_file():
                path_target_patterns_replaced = path_target_object.append_suffix('.PizzaCutter_Temp')
                with open(str(path_target_patterns_replaced), 'wb') as f_target:
                    self.replace_patterns_in_file(path_target_object, f_target)
                path_target_object.unlink()
                path_target_patterns_replaced.rename(path_target_object)

    def replace_patterns_in_file(self, path_source_file: pathlib.Path, f_target: BinaryIO) -> None:
        """
        replace all the patterns in the source file
        it is already prepared for the function that You can include the content of other files into one file -
        we dont know if we will ever finish that idea, because we simply can make that replacement in the config file
        """

        # this is already preparation when we are able to include the content of other files
        if path_source_file in self.file_stack:                                                                     # pragma: no cover
            raise RecursionError(f'Recursion on path includes : \n {pprint.pformat(self.file_stack)}')              # pragma: no cover
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
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_dir=path_template_dir, \
                                       path_target_dir=path_target_dir, \
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
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_dir=path_template_dir, \
                                       path_target_dir=path_target_dir, \
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
            raise RecursionError(f'"{self.pattern_stack[-1]}" refers back to "{pattern}"\n\nStack:\n{pprint.pformat(self.pattern_stack)}')

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
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_dir=path_template_dir, \
                                       path_target_dir=path_target_dir, \
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
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_expected_folder = path_test_dir / 'pizzacutter_test_project_01_expected'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)
        >>> path_target_dir.rmtree(ignore_errors=True)

        >>> # Test Create Files
        >>> pizza_cutter = PizzaCutter(path_conf_file=path_conf_file, \
                                       path_template_dir=path_template_dir, \
                                       path_target_dir=path_target_dir, \
                                       dry_run= False)
        >>> pizza_cutter.copy_files_from_template_to_project()
        >>> assert len(list(path_expected_folder.glob('./**/*'))) == len(list(path_target_dir.glob('./**/*')))

        >>> # Test Update Files
        >>> pizza_cutter.copy_files_from_template_to_project()
        >>> assert len(list(path_expected_folder.glob('./**/*'))) == len(list(path_target_dir.glob('./**/*')))

        >>> # Teardown
        >>> path_target_dir.rmtree(ignore_errors=True)


        """
        path_source_objects = self.get_path_template_objects()

        for path_source_object in path_source_objects:

            path_target_object_resolved = self.get_path_target_object(path_source_object=path_source_object)

            if self.do_not_copy(path_source_object):
                continue

            if self.skip_write_outside_project_folder(path_target_object_resolved):
                continue

            if self.skip_overwrite(path_source_object, path_target_object_resolved):
                continue

            if self.dry_run:
                continue

            if path_source_object.is_dir():
                path_target_object_resolved.mkdir(parents=True, exist_ok=True)
            else:
                path_target_object_resolved.parent.mkdir(parents=True, exist_ok=True)
                # because sometime we receive "permission denied" when overwriting the file (weired)
                path_target_object_resolved.unlink(missing_ok=True)
                path_source_object.copy2(path_target_object_resolved)

    def do_not_copy(self, file_object: pathlib.Path) -> bool:
        """ Check if the pattern for option 'object_no_copy' in file_object_name """
        file_object_name = str(file_object)
        if self.conf.pizza_cutter_options['object_no_copy'] in file_object_name:
            return True
        else:
            return False

    def skip_write_outside_project_folder(self, path_target_object: pathlib.Path, quiet: Optional[bool] = None) -> bool:
        """ Check if skipped because outside project folder not allowed """

        skip_outside_write = False

        if quiet is None:
            quiet = self.quiet

        if helpers.path_startswith(path_target_object, self.path_target_dir):
            return skip_outside_write

        if self.allow_outside_write:
            if self.dry_run:
                logger.info(f'object outside project directory: "{path_target_object}"')
            skip_outside_write = False
        else:
            msg = f'object outside project directory not allowed: "{path_target_object}"'
            if self.dry_run:
                logger.info(msg)
            else:
                if not quiet:
                    logger.warning(msg)
            skip_outside_write = True

        return skip_outside_write

    def skip_overwrite(self, path_source_object: pathlib.Path, path_target_object: pathlib.Path) -> bool:
        """ check if overwrite is allowed """

        if self.conf.pizza_cutter_options['object_no_overwrite'] in str(path_source_object) and path_target_object.exists():
            return True

        if path_target_object.exists():
            if self.allow_overwrite:
                if self.dry_run:
                    logger.debug(f'object will be overwritten: "{path_target_object}"')
                return False
            else:
                if self.dry_run:
                    logger.debug(f'object overwrite skipped, because allow_overwrite = False: "{path_target_object}"')
                return True
        else:
            return False

    def log_unfilled_patterns(self) -> None:

        path_source_objects = self.get_path_template_objects()

        for path_source_object in path_source_objects:

            path_target_object = self.get_path_target_object(path_source_object=path_source_object)

            if self.do_not_copy(path_source_object):
                continue

            if self.skip_write_outside_project_folder(path_target_object, quiet=True):
                continue

            self.log_unfilled_patterns_in_path(path_target_object)
            self.log_unfilled_pattern_in_object(path_target_object)

    def log_unfilled_patterns_in_path(self, _path: pathlib.Path) -> List[str]:
        """
        logs unfilled patterns in the path name of a file

        >>> # Setup
        >>> logger=logging.getLogger()
        >>> logging.basicConfig()
        >>> logger.level=logging.DEBUG

        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_02'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_02.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_02'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> path_test_file = pathlib.Path('some_file')
        >>> pizza_cutter.log_unfilled_patterns_in_path(path_test_file)
        []
        >>> path_test_file = pathlib.Path('some_file{{TestPizzaCutter}xy')
        >>> pizza_cutter.log_unfilled_patterns_in_path(path_test_file)
        ['missing closing brackets for "{{TestPizzaCutter"']

        >>> path_test_file = pathlib.Path('some_file{{TestPizzaCutter}}{{TestPizzaCutter.some.pattern}}xy')
        >>> pizza_cutter.log_unfilled_patterns_in_path(path_test_file)
        ['unfilled pattern "{{TestPizzaCutter}}"', 'unfilled pattern "{{TestPizzaCutter.some.pattern}}"']

        """

        str_path = str(_path)
        l_patterns: List[str] = list()
        # we think a pattern never will be that long
        max_pattern_length = 160
        for pattern_prefix in self.conf.pizzacutter_pattern_prefixes:
            if not self.quiet:
                for position in helpers.findall(pattern_prefix, str_path):
                    current_slice = str_path[position: position + max_pattern_length]
                    if '}}' not in current_slice:
                        l_patterns.append(f'missing closing brackets for "{pattern_prefix}"')
                    else:
                        full_pattern = current_slice.split('}}', 1)[0] + '}}'
                        l_patterns.append(f'unfilled pattern "{full_pattern}"')
                if l_patterns:
                    patterns = '\n'.join(l_patterns)
                    logger.warning(f'unfilled or malformed patterns in filename "{str_path}": \n{patterns}')
        return l_patterns

    def log_unfilled_pattern_in_object(self, path_object: pathlib.Path) -> List[str]:
        """
        find unfilled patterns in the file contents.
        we search for bytes, because we dont know the encoding of the file

        >>> # Setup
        >>> logger=logging.getLogger()
        >>> logging.basicConfig()
        >>> logger.level=logging.DEBUG

        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_02'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_02.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_02'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> # Test
        >>> path_test_file = path_template_dir / '{{TestPizzaCutter.project_dir}}/malformed.txt'
        >>> pizza_cutter.log_unfilled_pattern_in_object(path_test_file)
        ['missing closing brackets for "{{TestPizzaCutter.missing_brackets"', 'unfilled pattern "{{TestPizzaCutter.unfilled_pattern}}"']

        """
        l_patterns: List[str] = list()
        if path_object.is_file():
            # we think a pattern never will be that long
            max_pattern_length = 160
            content_bytes = path_object.read_bytes()
            for pattern_prefix in self.conf.pizzacutter_pattern_prefixes:
                pattern_prefix_bytes = pattern_prefix.encode('utf-8')
                for position in helpers.findall(pattern_prefix_bytes, content_bytes):
                    current_slice = content_bytes[position: position + max_pattern_length].split(b'\n', 1)[0]
                    if b'}}' not in current_slice:
                        current_slice = b'{{' + current_slice[2:].split(b'{{', 1)[0].split(b'}', 1)[0]
                        l_patterns.append(f'missing closing brackets for "{current_slice.decode("utf-8")}"')
                    else:
                        full_pattern_bytes = current_slice.split(b'}}', 1)[0] + b'}}'
                        l_patterns.append(f'unfilled pattern "{full_pattern_bytes.decode("utf-8")}"')
            if l_patterns:
                patterns = '\n'.join(l_patterns)
                logger.warning(f'unfilled or malformed patterns in file "{path_object}": \n{patterns}')
        return l_patterns

    def path_remove_cutter_option_patterns(self, path_source_file: pathlib.Path) -> pathlib.Path:
        """
        removes option patterns from the filename - those are already checked and considered earlier

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> # test ok
        >>> test_file = path_template_dir/ 'test.txt{{TestPizzaCutter.option.no_copy}}'
        >>> pizza_cutter.path_remove_cutter_option_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_template_01/test.txt')

        >>> # directory only option patterns Fails
        >>> test_file = path_template_dir/ '{{TestPizzaCutter.option.no_copy}}/test.txt{{TestPizzaCutter.option.no_copy}}'
        >>> pizza_cutter.path_remove_cutter_option_patterns(test_file)
        Traceback (most recent call last):
            ...
        RuntimeError: No part of the path ...

        >>> # File only option patterns Fails
        >>> test_file = path_template_dir/ '{{TestPizzaCutter.option.no_copy}}.test/{{TestPizzaCutter.option.no_copy}}'
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
                raise RuntimeError(f'No part of the path must consist ONLY of option patterns: "{path_source_file}"')
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
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> # test no replacements
        >>> test_file = path_template_dir/ 'test.txt'
        >>> pizza_cutter.path_replace_string_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_template_01/test.txt')

        >>> # test with replacement
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.doctest}}'] = 'doctest'
        >>> test_file = path_template_dir/ 'test_{{TestPizzaCutter.doctest}}.txt'
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

    def path_replace_pathlib_patterns(self, path_source_path: pathlib.Path) -> pathlib.Path:
        """
        Returns the resolved Target Path

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> # test absolute replacement + relative replacement
        >>> import platform
        >>> if platform.system().lower() == 'windows':
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.Path('c:/test/doctest_absolute')
        ... else:
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.Path('/test/doctest_absolute')
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.Path('./doctest')
        >>> test_file = path_template_dir/ '{{TestPizzaCutter.path.doctest.absolute}}/{{TestPizzaCutter.path.doctest.relative}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../doctest_absolute/doctest/test.txt')

        >>> # test no replacements
        >>> test_file = path_template_dir/ 'test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_project_01/test.txt')

        >>> # test relative replacements
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.Path('./doctest')
        >>> test_file = path_template_dir/ '{{TestPizzaCutter.path.doctest.relative}}/{{TestPizzaCutter.path.doctest.relative}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../tests/pizzacutter_test_project_01/doctest/doctest/test.txt')

        >>> # test relative replacement + absolute replacement
        >>> if platform.system().lower() == 'windows':
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.Path('c:/test/doctest_absolute')
        ... else:
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute}}'] = pathlib.Path('/test/doctest_absolute')
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.Path('./doctest')
        >>> test_file = path_template_dir/ '{{TestPizzaCutter.path.doctest.relative}}/{{TestPizzaCutter.path.doctest.absolute}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../doctest_absolute/test.txt')

        >>> # test absolute replacement + absolute replacement (last "wins")
        >>> if platform.system().lower() == 'windows':
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute1}}'] = pathlib.Path('c:/test/doctest_absolute1')
        ... else:
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute1}}'] = pathlib.Path('/test/doctest_absolute1')

        >>> if platform.system().lower() == 'windows':
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute2}}'] = pathlib.Path('c:/test/doctest_absolute2')
        ... else:
        ...     pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.absolute2}}'] = pathlib.Path('/test/doctest_absolute2')

        >>> test_file = path_template_dir/ '{{TestPizzaCutter.path.doctest.absolute1}}/{{TestPizzaCutter.path.doctest.absolute2}}/test.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        <BLANKLINE>
        ...Path('.../doctest_absolute2/test.txt')

        >>> # test path replacement not complete part of a path (name is also a complete part !!!)
        >>> pizza_cutter.conf.pizza_cutter_patterns['{{TestPizzaCutter.path.doctest.relative}}'] = pathlib.Path('./doctest')
        >>> test_file = path_template_dir/ '{{TestPizzaCutter.path.doctest.relative}}/{{TestPizzaCutter.path.doctest.relative}}.txt'
        >>> pizza_cutter.path_replace_pathlib_patterns(test_file)
        Traceback (most recent call last):
            ...
        RuntimeError: ... can only be one complete part of a path : ...{{...doctest.relative}}.txt", Pattern: {{TestPizzaCutter.path.doctest.relative}}

        """

        source_object_parts = reversed(path_source_path.parts)
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
                            f'pathlib.Path patterns can only be one complete part of a path : Path: "{path_source_path}", Pattern: {pattern}'
                            )
                    else:
                        target_object_part = pathlib.Path(replacement)
                        if target_object_part.is_absolute() and absolute_path_found:
                            logger.warning(
                                'the resulting path might be unexpected, You have more then one absolute pathlib.Path pattern in the path: '
                                f'"{path_source_path}", Pattern: "{pattern}" points to "{replacement}"')

            if not absolute_path_found:
                target_parts.append(target_object_part)
                if not isinstance(target_object_part, str) and pathlib.Path(target_object_part).is_absolute():
                    absolute_path_found = True

        target_parts = list(reversed(target_parts))
        path_target_path = pathlib.Path(*target_parts).resolve()

        if absolute_path_found:
            if not self.quiet:
                logger.warning('the resulting path of a template file might be unexpected, You have an absolute pathlib.Path pattern in the path: '
                               f'"{path_source_path}" points to "{path_target_path}"')
        else:
            path_target_path = path_target_path.replace_parts(self.path_template_dir.resolve(), self.path_target_dir.resolve())
        return path_target_path

    def get_path_template_subdirs_with_pattern(self) -> List[pathlib.Path]:
        """
        get the template sub directories with a valid pattern in it - all other directories are considered not to be part of the template

        >>> # Setup
        >>> path_test_dir = pathlib.Path(__file__).parent.parent / 'tests'
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'

        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> # TEST
        >>> pizza_cutter.get_path_template_subdirs_with_pattern()
        [...Path('.../pizzacutter_test_template_01/{{TestPizzaCutter.project_dir}}')...]

        """

        template_subdirs_with_pattern: List[pathlib.Path] = list()
        path_template_dir_subdirs = list(self.path_template_dir.glob('*/'))
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
        >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
        >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'
        >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01'
        >>> pizza_cutter = PizzaCutter(path_conf_file, path_template_dir, path_target_dir)

        >>> savedir = pathlib.Path.cwd().resolve()
        >>> os.chdir(path_template_dir)

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
          path_template_dir: Optional[pathlib.Path] = None,
          path_target_dir: Optional[pathlib.Path] = None,
          dry_run: Optional[bool] = None,
          allow_overwrite: Optional[bool] = None,
          allow_outside_write: Optional[bool] = None,
          quiet: Optional[bool] = None) -> None:

    pizza_cutter = PizzaCutter(path_conf_file=path_conf_file,
                               path_template_dir=path_template_dir,
                               path_target_dir=path_target_dir,
                               dry_run=dry_run,
                               allow_overwrite=allow_overwrite,
                               allow_outside_write=allow_outside_write,
                               quiet=quiet)

    pizza_cutter.build()


if __name__ == '__main__':
    print('this is a library only, the executable is named pizzacutter_cli.py')
