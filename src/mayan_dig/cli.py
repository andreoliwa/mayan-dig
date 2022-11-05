"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mmayan_dig` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``mayan_dig.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``mayan_dig.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os
from typing import Optional

import requests
import typer
from rich import print

app = typer.Typer()

session = requests.Session()
session.auth = os.environ["MAYAN_ADMIN_USER"], os.environ["MAYAN_ADMIN_PASSWORD"]
session.headers.update({"Accept": "application/json"})

MAYAN_URL = os.environ["MAYAN_URL"]


@app.command()
def cabinets(
    full_paths: Optional[list[str]] = typer.Argument(None, help="Partial path name to search"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose"),
):
    url = f"{MAYAN_URL}/api/v4/cabinets/"
    if verbose:
        print(f"[blue]Fetching all cabinets from[/blue] [yellow]{url}[/yellow]")

    selected = []
    while True:
        response = session.get(url)
        data = response.json()
        url = data["next"]
        if not url:
            break

        results = data["results"]
        for obj in results:
            # We don't need the hierarchy for now
            obj.pop("children")

            if not full_paths:
                selected.append(obj)
                continue

            for path in full_paths:
                if path.lower() in obj["full_path"].lower():
                    selected.append(obj)

    for obj in selected:
        print(f"[green]Cabinet:[/green] {obj['full_path']}")
        if verbose:
            print(obj)
