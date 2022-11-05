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
from pathlib import Path
from typing import Optional

import rich
import typer

from mayan_dig import Document
from mayan_dig import fetch_items_from
from mayan_dig import mayan_url_from_path

app = typer.Typer()


@app.command()
def cabinets(
    full_paths: Optional[list[str]] = typer.Argument(None, help="Partial path name to search"),
    download_dir: Path = typer.Option(
        None,
        "--download-dir",
        "-d",
        help="Download directory for the documents; if none, no documents will be downloaded",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
):
    if download_dir:
        rich.print(f"[yellow]Documents will be downloaded in[/yellow] [blue]{download_dir}[/blue]")
    else:
        rich.print("[yellow]No documents will be downloaded[/yellow]")

    selected_cabinets = []
    for cabinet_dict in fetch_items_from(mayan_url_from_path("cabinets"), verbose):
        # We don't need the hierarchy for now
        cabinet_dict.pop("children")

        if not full_paths:
            selected_cabinets.append(cabinet_dict)
            continue

        for path in full_paths:
            if path.lower() in cabinet_dict["full_path"].lower():
                selected_cabinets.append(cabinet_dict)
                continue

    for cabinet_dict in selected_cabinets:
        rich.print(f"[green]Cabinet:[/green] {cabinet_dict['full_path']}")
        if verbose:
            rich.print(cabinet_dict)

        if not download_dir:
            continue

        for document_dict in fetch_items_from(cabinet_dict["documents_url"], verbose):
            document = Document.from_json(document_dict)
            meta = set()
            for meta_dict in fetch_items_from(mayan_url_from_path(f"documents/{document.id}/metadata"), verbose):
                meta_dict.pop("document")
                key = meta_dict["metadata_type"]["label"]
                value = meta_dict["value"]
                meta.add(f"{key}-{value}")
                if verbose >= 2:
                    rich.print(meta_dict)

            rich_meta = f" [magenta]Metadata:[/magenta] {' '.join(sorted(meta))}" if meta else ""
            rich.print(
                f"  [cyan]Document:[/cyan] [magenta]Type:[/magenta] {document.doc_type}"
                f" [magenta]Name:[/magenta] {document.label_or_filename}"
                f" [magenta]Created:[/magenta] {document.created_at}{rich_meta}"
            )
            if verbose:
                rich.print(document)
            if verbose >= 2:
                rich.print(document_dict)
            # FIXME: actually download the document and save the file
