# STDLIB
import pathlib3x as pathlib  # type: ignore


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

    """

    return bool(path_object_to_test.resolve().is_relative_to(path_object.resolve()))


def create_target_directory(path_target_file_object: pathlib.Path) -> None:
    """
    if not path_target_file_object.is_dir():
        path_target_file_object = path_target_file_object.parent
    """
    path_target_file_object.mkdir(parents=True, exist_ok=True)


def replace_source_dir_path_with_target_dir_path(pathlib_path: pathlib.Path, path_source_dir: pathlib.Path, path_target_dir: pathlib.Path) -> pathlib.Path:
    """
    TODO: put it in pathlib3x

    >>> pathlib_path = pathlib.Path('/some/really/complicated/path/complicated/path.txt')
    >>> path_source_dir = pathlib.Path('/some/really')
    >>> path_target_dir = pathlib.Path('/some/really/really')

    >>> # test ok
    >>> replace_source_dir_path_with_target_dir_path(pathlib_path, path_source_dir, path_target_dir)
    <BLANKLINE>
    ...Path('...some/really/really/complicated/path/complicated/path.txt')

    >>> # test not both the same relative / absolute
    >>> path_source_dir = pathlib.Path('./some/really')
    >>> replace_source_dir_path_with_target_dir_path(pathlib_path, path_source_dir, path_target_dir)
    Traceback (most recent call last):
        ...
    ValueError: Source and Target Directory need to be both absolute or both relative

    """

    if not path_source_dir.is_absolute() == path_target_dir.is_absolute():
        raise ValueError('Source and Target Directory need to be both absolute or both relative')

    str_pathlib_path = str(pathlib_path.resolve())
    str_path_source_dir = str(path_source_dir.resolve())
    str_path_target_dir = str(path_target_dir.resolve())

    if not str_pathlib_path.startswith(str_path_source_dir):
        raise ValueError('Source Dir Replacement, the path "{pathlib_path}" needs to start with the source path "{path_source_dir}"'.format(
            pathlib_path=pathlib_path, path_source_dir=path_source_dir))

    result = str_pathlib_path.replace(str_path_source_dir, str_path_target_dir, 1)
    return pathlib.Path(result)
