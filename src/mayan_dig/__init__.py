__version__ = "0.0.0"

import os
import unicodedata
from dataclasses import dataclass

import requests
import rich

session = requests.Session()
session.auth = os.environ["MAYAN_ADMIN_USER"], os.environ["MAYAN_ADMIN_PASSWORD"]
session.headers.update({"Accept": "application/json"})

MAYAN_URL = os.environ["MAYAN_URL"]


@dataclass
class Document:
    id: int
    doc_type: str
    download_url: str
    label: str
    filename: str
    created_at: str
    description: str

    @classmethod
    def from_json(cls, data: dict):
        label = data["label"]
        filename = data["file_latest"]["filename"]
        if label != filename:
            raise ValueError(f"Mismatch! {label=} {filename=}")
        return cls(
            id=data["id"],
            doc_type=data["document_type"]["label"],
            download_url=data["file_latest"]["download_url"],
            label=label,
            filename=filename,
            created_at=data["datetime_created"],
            description=data["description"],
        )


def mayan_url_from_path(url_path: str) -> str:
    return f"{MAYAN_URL}/api/v4/{url_path}/"


def fetch_items_from(url: str, verbose=False):
    while True:
        if verbose:
            rich.print(f"[yellow]Fetching items from[/yellow] [blue]{url}[/blue]")
        response = session.get(url)
        data = response.json()
        yield from data["results"]
        url = data["next"]
        if not url:
            break


def remove_control_characters(text: str) -> str:
    """Adapted from https://stackoverflow.com/a/19016117."""
    return "".join(char for char in text if unicodedata.category(char)[0] != "C")
