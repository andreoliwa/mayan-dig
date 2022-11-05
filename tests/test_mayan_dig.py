from typer.testing import CliRunner

from mayan_dig import remove_control_characters
from mayan_dig.cli import app


def test_main():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    for line in [
        "Usage: cabinets [OPTIONS] [FULL_PATHS]...",
        "full_paths      [FULL_PATHS]...  Partial path name to search",
    ]:
        assert line in remove_control_characters(result.output)
    assert result.exit_code == 0
