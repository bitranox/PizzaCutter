# STDLIB
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
