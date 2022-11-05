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
from mayan_dig import session
from mayan_dig.constants import DOC_CREATED
from mayan_dig.constants import DOC_NAME
from mayan_dig.constants import DOC_TYPE
from mayan_dig.constants import DOWNLOAD_DIR
from mayan_dig.constants import META_PREFIX

app = typer.Typer()


@app.command()
def cabinets(
    full_paths: Optional[list[str]] = typer.Argument(None, help="Partial path name to search"),
    documents: bool = typer.Option(False, "--docs", "-o", help="Display documents in cabinets"),
    download_dir: Path = typer.Option(
        None,
        f"--{DOWNLOAD_DIR}",
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
    # Display documents if a download dir was chosen
    if download_dir:
        documents = True

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

        if not documents:
            continue

        for document_dict in fetch_items_from(cabinet_dict["documents_url"], verbose):
            document = Document.from_json(document_dict)
            meta = set()
            for meta_dict in fetch_items_from(mayan_url_from_path(f"documents/{document.id}/metadata"), verbose):
                meta_dict.pop("document")
                key = meta_dict["metadata_type"]["name"]
                value = meta_dict["value"]
                meta.add(f"[magenta]{META_PREFIX}{key}:[/magenta] {value}")
                if verbose >= 2:
                    rich.print(meta_dict)

            rich_meta = " ".join(sorted(meta)) if meta else ""
            rich.print(
                f"  [yellow]Document:[/yellow] [magenta]{DOC_TYPE}:[/magenta] {document.doc_type}"
                f" [magenta]{DOC_NAME}:[/magenta] {document.label}"
                f" [magenta]{DOC_CREATED}:[/magenta] {document.created_at} {rich_meta}"
            )
            if verbose:
                rich.print(document)
            if verbose >= 2:
                rich.print(document_dict)

            if download_dir:
                downloaded_file_path = download_dir / document.filename
                message = "Downloading to"
            else:
                downloaded_file_path = f"<{DOWNLOAD_DIR}>/{document.filename}"
                message = "Would be downloaded as"
            rich.print(f"    {message} [blue]{downloaded_file_path}[/blue]")

            if download_dir:
                response = session.get(document.download_url)
                try:
                    # TODO: set modified and created dates
                    downloaded_file_path.write_bytes(response.content)
                except Exception as err:
                    rich.print(err)
