from typer.testing import CliRunner

from mayan_dig.cli import app


def test_main():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert "Usage: cabinets [OPTIONS] [FULL_PATHS]..." in result.output
    assert result.exit_code == 0
