# STDLIB
import logging
import pathlib3x as pathlib
from typing import Iterable, Union


def path_startswith(path_object_to_test: pathlib.Path, path_object: pathlib.Path) -> bool:
    """
    tests if the "path_object_to_test" starts with path_object
    we resolve here before, because symlinks might be involved

    >>> source_folder = pathlib.Path('/test1/test2')

    >>> test_folder1 =  pathlib.Path('/test1')
    >>> test_folder2 =  pathlib.Path('/test2/test1')
    >>> test_folder3 =  pathlib.Path('/test1/test2')
    >>> test_folder4 =  pathlib.Path('/test1/test2/test3')
    >>> assert not path_startswith(test_folder1, source_folder)
    >>> assert not path_startswith(test_folder2, source_folder)
    >>> assert path_startswith(test_folder3, source_folder)
    >>> assert path_startswith(test_folder4, source_folder)

    >>> test_folder1 =  pathlib.Path('/test1')
    >>> test_folder2 =  pathlib.Path('/test2/test1')

    """
    return bool(path_object_to_test.resolve().is_relative_to(path_object.resolve()))


def findall(pattern: Union[str, bytes], text: Union[str, bytes]) -> Iterable[int]:
    """
    Yields all the positions of the pattern in the text

    >>> list(findall('{{test}}', 'my{{test}}{{test}}'))
    [2, 10]
    >>> list(findall('{{text}}', 'my{{test}}{{test}}'))
    []
    >>> list(findall('{{test}}'.encode(), 'my{{test}}{{test}}'.encode()))
    [2, 10]
    >>> list(findall('{{test}}'.encode(), 'my{{test}}\\n{{test}}'.encode()))
    [2, 11]

    """
    i = text.find(pattern)                  # type: ignore
    while i != -1:
        yield i
        i = text.find(pattern, i + 1)       # type: ignore


# find_version_number_in_file{{{
def find_version_number_in_file(path_txt_file: pathlib.Path) -> str:
    """
    this function can be used in the PizzaCutter Template to extrect the Version Numer
    from a text file (usually CHANGES.rst)

    it finds the first line in a file, where the first non-blank character is a digit or v<digit>.
    the whole string (until ':' or EOL) is returned.

    if the version number or the file can not be found, Version 'v0.0.1a0' will be returned
    and a warning will be logged


    Parameter
    ---------
    path_txt_file
        the text file to search for

    Examples
    --------
    File content:

        some
        text
        1.2.3a0:  # or v1.2.3a0

    Output :
        1.2.3a0  # or v1.2.3a0


    >>> path_test_dir = pathlib.Path(__file__).parent.parent.parent.resolve() / 'tests'
    >>> path_test_file = path_test_dir / 'test_find_version_number_in_file.txt'
    >>> path_test_file_no_version = path_test_dir / 'test_find_version_number_in_file_no_version.txt'
    >>> path_test_file_not_existing = path_test_dir / 'non_existing_file.txt'
    >>> assert find_version_number_in_file(path_test_file) == '1.2.3a4'
    >>> assert find_version_number_in_file(path_test_file_no_version) == 'v0.0.1a0'
    >>> assert find_version_number_in_file(path_test_file_not_existing) == 'v0.0.1a0'

    """
    # find_version_number_in_file}}}

    result = 'v0.0.1a0'
    try:
        with open(str(path_txt_file), 'r', encoding='utf-8-sig') as f:
            line = f.readline()
            while line:
                line = line.strip()
                try:
                    if line:
                        if line[0].lower() == 'v':
                            int(line[1])
                        else:
                            int(line[0])
                        result = line.split(':')[0].strip()
                        break
                except (ValueError, IndexError):
                    pass
                line = f.readline()
    except FileNotFoundError:
        logging.getLogger().warning(f'no Version number found in "{path_txt_file}", file not found, assuming Version "v0.0.1a0"')
        return result

    if result == 'v0.0.1a0':
        logging.getLogger().warning(f'no Version number found in "{path_txt_file}", assuming Version "v0.0.1a0"')
    return result
