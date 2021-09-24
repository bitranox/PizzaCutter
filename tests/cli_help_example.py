# STDLIB
from typing import Dict, List
# EXT
import click

# CONSTANTS
CLICK_CONTEXT_SETTINGS: Dict[str, List[str]] = dict(help_option_names=['-h', '--help'])
CLICK_CONTEXT_SETTINGS_NO_HELP: Dict[str, List[str]] = dict(help_option_names=[])


@click.group(help='some help', context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version='1.1.1',
                      prog_name='program name',
                      message=f"{'cli command'} version %(version)s")
def cli_main() -> None:             # pragma: no cover
    pass                            # pragma: no cover


# command1 without arguments and options
@cli_main.command('command1', context_settings=CLICK_CONTEXT_SETTINGS_NO_HELP)
def cli_command1() -> None:         # pragma: no cover
    """ command1 without arguments and options """
    pass


# command2 with arguments
@cli_main.command('command2', context_settings=CLICK_CONTEXT_SETTINGS)
@click.argument('argument1')
@click.argument('argument2')
def cli_command2(argument1: str, argument2: str) -> None:
    """ command2 with arguments """
    pass                            # pragma: no cover


# command3 with arguments and options
@cli_main.command('command3', context_settings=CLICK_CONTEXT_SETTINGS)
@click.argument('argument1')
@click.argument('argument2')
@click.option('-a', '--a_option', is_flag=True)             # no help here
@click.option('-b', '--b_option', type=int, default=-1, help='help for b_option')
@click.option('-c', '--c_option', help='help for c_option')
def cli_command3(argument1: str, argument2: str, a_option: bool, b_option: int, c_option: str) -> None:
    """\b
        command3 with multi
        line help arguments and options
        """
    pass                            # pragma: no cover


# command4 with arguments, options and sub_command
# groups must not have arguments or we can not parse them
# because to get help for the sub command we need to put :
# program command4 arg1 arg2 command5 -h
# and we dont know the correct type of arg1, arg2

@cli_main.group('command4', context_settings=CLICK_CONTEXT_SETTINGS)
@click.argument('argument1')
@click.argument('argument2')
@click.option('-a', '--a_option', is_flag=True)             # no help here
@click.option('-b', '--b_option', type=int, default=-1, help='help for b_option')
@click.option('-c', '--c_option', help='help for c_option')
def cli_command4(argument1: str, argument2: str, a_option: bool, b_option: int, c_option: str) -> None:
    """\b
     command4 with arguments,
     options and sub_command
     and a very long
     multiline help
     what for sure will not fit into one terminal line
     what for sure will not fit into one terminal line
     what for sure will not fit into one terminal line
     what for sure will not fit into one terminal line
     """
    pass                            # pragma: no cover


# command5, sub_command of command4 with arguments, options
@cli_command4.command('command5', context_settings=CLICK_CONTEXT_SETTINGS)
@click.argument('argument1')
@click.argument('argument2')
@click.option('-a', '--a_option', is_flag=True)             # no help here
@click.option('-b', '--b_option', type=int, default=-1, help='help for b_option')
@click.option('-c', '--c_option', help='help for c_option')
def cli_command5(argument1: str, argument2: str, a_option: bool, b_option: int, c_option: str) -> None:
    """command5, sub_command of command4 with arguments, options"""
    pass                            # pragma: no cover


# entry point if main
if __name__ == '__main__':
    cli_main()
