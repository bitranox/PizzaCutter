# STDLIB
import pathlib3x as pathlib


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
    return bool(path_object_to_test.resolve().is_relative_to(str(path_object.resolve())))


def create_target_directory(path_target_file_object: pathlib.Path) -> None:
    """
    if not path_target_file_object.is_dir():
        path_target_file_object = path_target_file_object.parent
    """
    path_target_file_object.mkdir(parents=True, exist_ok=True)
