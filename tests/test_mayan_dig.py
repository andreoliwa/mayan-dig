from typer.testing import CliRunner

from mayan_dig.cli import app

# https://typer.tiangolo.com/tutorial/commands/help/#rich-markdown-and-markup
app.rich_markup_mode = None


def test_main():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    for line in [
        "Usage: cabinets [OPTIONS] [FULL_PATHS]...",
        "full_paths      [FULL_PATHS]...  Partial path name to search",
    ]:
        assert line in result.output
    assert result.exit_code == 0
