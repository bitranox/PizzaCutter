# STDLIB
import importlib
import importlib.util
import pathlib3x as pathlib
import sys
from typing import Union


def import_module_from_file(module_fullpath: Union[pathlib.Path, str], reload: bool = False):   # type: ignore
    """
    TODO : replace with lib_import when avail maybe take from pycharm, there we do the full coverage ...

    >>> # re-import from file
    >>> import_module_from_file(pathlib.Path(__file__))
    <module 'import_module' from '...import_module.py'>

    >>> # re-import from file without extension
    >>> import_module_from_file(pathlib.Path(__file__).with_suffix(''))
    <module 'import_module' from '...import_module.py'>

    >>> # re-import from file, reload = True
    >>> import_module_from_file(pathlib.Path(__file__), reload=True)
    <module 'import_module' from '...import_module.py'>

    >>> # import from non-existing file, and invalid module name. reload = True

    >>> # re-import from non-existing file, but already imported module name. reload = True
    >>> import_module_from_file(pathlib.Path(__file__).with_suffix('.non_existing'), reload=True)
    Traceback (most recent call last):
    ...
    FileNotFoundError: module "...import_module.non_existing.py" not found

    """
    module_fullpath = pathlib.Path(module_fullpath)

    if not module_fullpath.suffix == '.py':
        module_fullpath = pathlib.Path(str(module_fullpath) + '.py')

    if not module_fullpath.is_file():
        raise FileNotFoundError('module "{}" not found'.format(module_fullpath))

    module_name = module_fullpath.stem

    if not reload and module_name in sys.modules:
        return sys.modules[module_name]

    if reload:
        # see https://docs.python.org/3/library/importlib.html
        importlib.invalidate_caches()

    sys.path.append(str(module_fullpath.parent))

    spec = importlib.util.spec_from_file_location(module_name, module_fullpath)
    if spec is None:
        sys.path.pop()
        raise ImportError('can not get spec from file location "{}"'.format(module_fullpath))

    try:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
    except Exception as exc:
        raise ImportError('can not load module "{}"'.format(module_name)) from exc
    finally:
        sys.path.pop()
        sys.path.append(str(module_fullpath.parent))

    try:
        spec.loader.exec_module(mod)    # type: ignore
    except Exception as exc:
        sys.path.pop()
        raise ImportWarning('module "{}" reloaded, but can not be executed'.format(module_name)) from exc

    return mod
