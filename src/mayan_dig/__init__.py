__version__ = "0.0.0"

import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pendulum
import requests
import rich

from mayan_dig.settings import MAYAN_DIG_PASSWORD
from mayan_dig.settings import MAYAN_DIG_URL
from mayan_dig.settings import MAYAN_DIG_USER

session = requests.Session()
session.auth = MAYAN_DIG_USER, MAYAN_DIG_PASSWORD
session.headers.update({"Accept": "application/json"})


@dataclass
class Document:
    id: int
    doc_type: str
    download_url: str
    name: str
    created_at: pendulum.DateTime
    description: str

    def __post_init__(self):
        self.path = Path(self.name)

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
            name=label,
            created_at=pendulum.parse(data["datetime_created"]),
            description=data["description"],
        )

    @property
    def stem(self):
        return self.path.stem

    @property
    def suffix(self):
        return self.path.suffix


def mayan_url_from_path(url_path: str) -> str:
    return f"{MAYAN_DIG_URL}/api/v4/{url_path}/"


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
