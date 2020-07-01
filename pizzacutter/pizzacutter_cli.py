# STDLIB
import pathlib

# EXT
import click

# CONSTANTS
CLICK_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

try:
    from . import __init__conf__
    from . import pizzacutter
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    # imports for pytest
    import __init__conf__                   # type: ignore  # pragma: no cover
    import pizzacutter                      # type: ignore  # pragma: no cover


def info() -> None:
    """
    >>> info()
    Info for ...

    """
    __init__conf__.print_info()


def rebuild(conf_file: str, template_dir: str = '', project_dir: str = '', dry_run: bool = False, overwrite: bool = False, write_outside: bool = False) -> None:

    path_conf_file = pathlib.Path(conf_file).resolve()

    if template_dir:
        path_template_folder = pathlib.Path(template_dir).resolve()
    else:
        path_template_folder = path_conf_file.parent

    if project_dir:
        path_project_folder = pathlib.Path(project_dir).resolve()
    else:
        path_project_folder = pathlib.Path.cwd().resolve()

    pizzacutter.build(path_conf_file=path_conf_file, path_template_folder=path_template_folder, path_target_folder=path_project_folder,
                      dry_run=dry_run, allow_overwrite=overwrite, allow_outside_write=write_outside)


@click.group(help=__init__conf__.title, context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version=__init__conf__.version,
                      prog_name=__init__conf__.shell_command,
                      message='{} version %(version)s'.format(__init__conf__.shell_command))
def cli_main() -> None:             # pragma: no cover
    pass


@cli_main.command('info', context_settings=CLICK_CONTEXT_SETTINGS)
def cli_info() -> None:             # pragma: no cover
    """ get program informations """
    info()                          # pragma: no cover


@cli_main.command('rebuild', context_settings=CLICK_CONTEXT_SETTINGS)
@click.argument('conf_file', type=click.Path(dir_okay=False, file_okay=True, exists=True, readable=True, resolve_path=True))
@click.option('-t', '--template_dir', type=click.Path(dir_okay=True, file_okay=False, exists=False, resolve_path=False),
              help='use different template Folder with given CONF_FILE', default='')
@click.option('-p', '--project_dir', type=click.Path(dir_okay=True, file_okay=False, exists=False, resolve_path=False),
              help='set target directory, default: current directory', default='')
@click.option('-d', '--dry_run', is_flag=True, help='dry run', default=False)
@click.option('-o', '--overwrite', is_flag=True, help='allow overwriting of files', default=False)
@click.option('-w', '--write_outside', is_flag=True, help='allow write outside the project dir', default=False)
def cli_rebuild(conf_file: str, template_dir: str = '', project_dir: str = '',
                dry_run: bool = False, overwrite: bool = False, write_outside: bool = False) -> None:
    """ build or rebuild from CONF_FILE"""
    rebuild(conf_file=conf_file, template_dir=template_dir, project_dir=project_dir, dry_run=dry_run, overwrite=overwrite, write_outside=write_outside)


# entry point if main
if __name__ == '__main__':
    cli_main()
