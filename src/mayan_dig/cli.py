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
import shutil
import string
from pathlib import Path
from typing import Optional

import rich
import typer

from mayan_dig import Document
from mayan_dig import fetch_items_from
from mayan_dig import mayan_url_from_path
from mayan_dig import session
from mayan_dig.constants import DOC_CABINET
from mayan_dig.constants import DOC_CREATED
from mayan_dig.constants import DOC_NAME
from mayan_dig.constants import DOC_STEM
from mayan_dig.constants import DOC_SUFFIX
from mayan_dig.constants import DOC_TYPE
from mayan_dig.constants import DOWNLOAD_DIR
from mayan_dig.constants import META_PREFIX
from mayan_dig.constants import PROJECT_NAME
from mayan_dig.settings import MAYAN_DIG_PATH_TEMPLATE

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
    delete_dir: bool = typer.Option(False, help="Delete download dir before starting, with a prompt"),
    overwrite: bool = typer.Option(False, help="Overwrite existing files"),
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
):
    # Display documents if a download dir was chosen
    if download_dir:
        documents = True

        # Delete dir if it exists
        mayan_dig_dir = download_dir / PROJECT_NAME
        if delete_dir and mayan_dig_dir.exists():
            confirmation = typer.confirm(f"Are you sure you want to delete it {mayan_dig_dir}?")
            if confirmation:
                shutil.rmtree(mayan_dig_dir)

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

    template = string.Template(MAYAN_DIG_PATH_TEMPLATE)
    rich.print(f"Using this path template: [bright_green]{MAYAN_DIG_PATH_TEMPLATE}[/bright_green]")

    for cabinet_dict in selected_cabinets:
        cabinet = cabinet_dict["full_path"]
        rich.print(f"[magenta]{DOC_CABINET}:[/magenta] {cabinet}")
        if verbose:
            rich.print(cabinet_dict)

        if not documents:
            continue

        for document_dict in fetch_items_from(cabinet_dict["documents_url"], verbose):
            document = Document.from_json(document_dict)
            meta = set()
            for meta_dict in fetch_items_from(mayan_url_from_path(f"documents/{document.id}/metadata"), verbose):
                meta_dict.pop("document")
                key = META_PREFIX + meta_dict["metadata_type"]["name"]
                value = meta_dict["value"]
                meta.add((key.lower(), value))
                if verbose >= 2:
                    rich.print(meta_dict)

            mapping = {
                DOC_CABINET: cabinet,
                DOC_TYPE: document.doc_type,
                DOC_NAME: document.name,
                DOC_STEM: document.stem,
                DOC_SUFFIX: document.suffix,
                # For template purposes, use only the date part of the creation time.
                # Hardcoded for now, but it can become a setting if needed
                DOC_CREATED: document.created_at.date().isoformat(),
            }
            for pair in sorted(meta):
                mapping[pair[0]] = pair[1]

            templated_file_path = template.safe_substitute(mapping).replace(":", "-")
            skip = False
            if download_dir:
                downloaded_file_path = download_dir / PROJECT_NAME / templated_file_path
                message = "[green]Downloading document as[/green]"

                if downloaded_file_path.exists() and not overwrite:
                    message = "[red]Skipping existing document at[/red]"
                    skip = True
            else:
                downloaded_file_path = Path(f"<{DOWNLOAD_DIR}>") / PROJECT_NAME / templated_file_path
                message = "[yellow]Document would be downloaded as[/yellow]"

            rich.print(f"  {message} [blue]{downloaded_file_path}[/blue]")
            rich_mapping = []
            for key, value in mapping.items():
                rich_mapping.append(f"    [magenta]{key}:[/magenta] {value}")
            rich.print("\n".join(rich_mapping))

            if verbose:
                rich.print(document)
            if verbose >= 2:
                rich.print(document_dict)

            if download_dir and not skip:
                response = session.get(document.download_url)
                try:
                    downloaded_file_path.parent.mkdir(parents=True, exist_ok=True)
                    downloaded_file_path.write_bytes(response.content)

                    # Set created and modified dates on the downloaded file
                    mtime = document.created_at.int_timestamp
                    os.utime(downloaded_file_path, (mtime, mtime))
                except Exception as err:
                    rich.print(err)
