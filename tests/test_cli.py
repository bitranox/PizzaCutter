# EXT
from click.testing import CliRunner

# OWN
import pizzacutter.pizzacutter_cli as pizzacutter_cli

runner = CliRunner()
runner.invoke(pizzacutter_cli.cli_main, ['--version'])
runner.invoke(pizzacutter_cli.cli_main, ['-h'])
runner.invoke(pizzacutter_cli.cli_main, ['info'])
