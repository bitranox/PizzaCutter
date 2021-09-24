# STDLIB
import pathlib3x as pathlib
import sys
from typing import Optional

# EXT
import click

# OWN
import cli_exit_tools

# PROJ
try:
    from . import __init__conf__
    from . import pizzacutter
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    # imports for pytest
    import __init__conf__                   # type: ignore  # pragma: no cover
    import pizzacutter                      # type: ignore  # pragma: no cover

# CONSTANTS
CLICK_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def info() -> None:
    """
    >>> info()
    Info for ...

    """
    __init__conf__.print_info()


def build(conf_file: str, template_dir: str = '', target_dir: str = '', dry_run: bool = False, overwrite: bool = False, write_outside: bool = False) -> None:
    """ Builds the Project from the Template

    >>> # Setup
    >>> path_test_dir = pathlib.Path(__file__).parent.parent.resolve() / 'tests'
    >>> path_template_dir = path_test_dir / 'pizzacutter_test_template_01'
    >>> path_target_dir = path_test_dir / 'pizzacutter_test_project_01_result'
    >>> path_conf_file = path_template_dir / 'PizzaCutterTestConfig_01.py'

    >>> # Test only pass "conf_file", dry run
    >>> build(conf_file=str(path_conf_file), template_dir='', target_dir='', dry_run=True)

    >>> # Test pass "conf_file", "template_dir" and "target_dir" dry run
    >>> build(conf_file=str(path_conf_file), template_dir=str(path_template_dir), target_dir=str(path_target_dir), dry_run=True)

    """

    path_conf_file = pathlib.Path(conf_file).resolve()

    if template_dir:
        path_template_dir = pathlib.Path(template_dir).resolve()
    else:
        path_template_dir = path_conf_file.parent

    if target_dir:
        path_target_dir = pathlib.Path(target_dir).resolve()
    else:
        path_target_dir = pathlib.Path.cwd().resolve()

    pizzacutter.build(path_conf_file=path_conf_file, path_template_dir=path_template_dir, path_target_dir=path_target_dir,
                      dry_run=dry_run, allow_overwrite=overwrite, allow_outside_write=write_outside)


@click.group(help=__init__conf__.title, context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version=__init__conf__.version,
                      prog_name=__init__conf__.shell_command,
                      message=f'{__init__conf__.shell_command} version {__init__conf__.version}')
@click.option('--traceback/--no-traceback', is_flag=True, type=bool, default=None, help='return traceback information on cli')
def cli_main(traceback: Optional[bool] = None) -> None:
    if traceback is not None:
        cli_exit_tools.config.traceback = traceback


@cli_main.command('info', context_settings=CLICK_CONTEXT_SETTINGS)
def cli_info() -> None:
    """ get program informations """
    info()


@cli_main.command('build', context_settings=CLICK_CONTEXT_SETTINGS)
@click.argument('conf_file', type=click.Path(dir_okay=False, file_okay=True, exists=True, readable=True, resolve_path=True))
@click.option('-p', '--template_dir', type=click.Path(dir_okay=True, file_okay=False, exists=False, resolve_path=False),
              help='use different template Folder with given CONF_FILE', default='')
@click.option('-t', '--target_dir', type=click.Path(dir_okay=True, file_okay=False, exists=False, resolve_path=False),
              help='set target directory, default: current directory', default='')
@click.option('-d', '--dry_run', is_flag=True, help='dry run', default=False)
@click.option('-o', '--overwrite', is_flag=True, help='allow overwriting of files', default=True)
@click.option('-w', '--write_outside', is_flag=True, help='allow write outside the project dir', default=False)
def cli_build(conf_file: str, template_dir: str = '', target_dir: str = '',
              dry_run: bool = False, overwrite: bool = False, write_outside: bool = False) -> None:
    """ build or rebuild from CONF_FILE"""
    build(conf_file=conf_file,
          template_dir=template_dir,
          target_dir=target_dir,
          dry_run=dry_run,
          overwrite=overwrite,
          write_outside=write_outside)


# entry point if main
if __name__ == '__main__':
    try:
        cli_main()
    except Exception as exc:
        cli_exit_tools.print_exception_message()
        sys.exit(cli_exit_tools.get_system_exit_code(exc))
    finally:
        cli_exit_tools.flush_streams()
