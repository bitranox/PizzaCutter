# STDLIB
import importlib
import importlib.util
import pathlib
import sys
from typing import Union


def import_module_from_file(module_fullpath: Union[pathlib.Path, str], reload: bool = False):   # type: ignore
    """
    TODO : replace with lib_import when avail maybe take from pycharm
    """
    module_fullpath = pathlib.Path(module_fullpath)

    if not module_fullpath.suffix == '.py':
        module_fullpath = pathlib.Path(str(module_fullpath) + '.py')

    module_name = module_fullpath.stem

    if not reload and module_name in sys.modules:
        return sys.modules[module_name]

    if reload:
        invalidate_caches()

    if sys.version_info < (3, 6):
        sys.path.append(str(module_fullpath.parent))
        mod = importlib.import_module(module_name)
        sys.path.pop()
        sys.modules[module_name] = mod

    else:
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


def invalidate_caches() -> None:    # see https://docs.python.org/3/library/importlib.html
    if sys.version_info >= (3, 3):
        importlib.invalidate_caches()
