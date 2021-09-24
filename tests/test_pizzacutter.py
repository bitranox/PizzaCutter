# STDLIB
import pytest                   # type: ignore
import shutil
from typing import Any
import logging

# OWN
import pathlib3x as pathlib

# proj
import pizzacutter

logger = logging.getLogger()


@pytest.fixture(scope="function")
def pizza_cutter_instance():
    path_test_dir = pathlib.Path(__file__).parent.parent.resolve() / 'tests'
    path_template_dir = path_test_dir / 'pizzacutter_test_template_02'
    path_conf_file = path_template_dir / 'PizzaCutterTestConfig_02.py'
    path_target_dir = path_test_dir / 'test_target'
    path_outside_target_dir = get_outside_target_dir()

    pizza_cutter = pizzacutter.PizzaCutter(path_conf_file=path_conf_file, path_template_dir=path_template_dir, path_target_dir=path_target_dir)
    yield pizza_cutter  # provide the fixture value
    # teardown code
    if not path_target_dir.is_relative_to(path_test_dir):
        raise RuntimeError(f'attempt to delete "{pizza_cutter_instance.path_target_dir}" which is outside the test dir "{path_test_dir}"')

    if not path_target_dir.is_relative_to(path_test_dir):
        raise RuntimeError(f'attempt to delete "{path_outside_target_dir}" which is outside the test dir "{path_test_dir}"')

    shutil.rmtree(path_target_dir, ignore_errors=True)
    shutil.rmtree(path_outside_target_dir, ignore_errors=True)


@pytest.fixture(params=[False, True], ids=['quiet=False', 'quiet=True'])
def pizza_cutter_quiet(request: Any) -> bool:
    return request.param


@pytest.fixture(params=[False, True], ids=['dry_run=False', 'dry_run=True'])
def pizza_cutter_dry_run(request: Any) -> bool:
    return request.param


@pytest.fixture(params=[False, True], ids=['allow_overwrite=False', 'allow_overwrite=True'])
def pizza_cutter_allow_overwrite(request: Any) -> bool:
    return request.param


@pytest.fixture(params=[False, True], ids=['allow_outside_write=False', 'allow_outside_write=True'])
def pizza_cutter_allow_outside_write(request: Any) -> bool:
    return request.param


def test_pizzacutter(pizza_cutter_instance, pizza_cutter_quiet, pizza_cutter_dry_run, pizza_cutter_allow_overwrite, pizza_cutter_allow_outside_write):
    # now the text matrix
    pizza_cutter_instance.quiet = pizza_cutter_quiet
    pizza_cutter_instance.dry_run = pizza_cutter_dry_run
    pizza_cutter_instance.allow_overwrite = pizza_cutter_allow_overwrite
    pizza_cutter_instance.allow_outside_write = pizza_cutter_allow_outside_write
    pizza_cutter_instance.build()
    # do it a second time to trigger check overwrite functions
    pizza_cutter_instance.build()
    assert pizza_cutter_instance.path_target_dir.exists() is not pizza_cutter_instance.dry_run
    assert get_outside_target_dir().exists() == (pizza_cutter_allow_outside_write and not pizza_cutter_dry_run)
    # test dry_run on an existing target
    if pizza_cutter_dry_run:
        pizza_cutter_instance.dry_run = False
        pizza_cutter_instance.build()
        pizza_cutter_instance.dry_run = True
        pizza_cutter_instance.build()


def get_outside_target_dir() -> pathlib.Path:
    path_test_dir = pathlib.Path(__file__).parent.parent.resolve() / 'tests'
    outside_target_dir = path_test_dir / 'outside_target_dir'
    return outside_target_dir
