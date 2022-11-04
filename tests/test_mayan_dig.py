from click.testing import CliRunner

from mayan_dig.cli import cabinets


def test_main():
    runner = CliRunner()
    result = runner.invoke(cabinets, [])

    assert result.output == "()\n"
    assert result.exit_code == 0
