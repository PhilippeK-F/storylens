from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


@dataclass(frozen=True)
class ImdbFile:
    name: str  # e.g. "title.basics.tsv.gz"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: Path, timeout: int = 60) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Skip if exists
    if dest.exists() and dest.stat().st_size > 0:
        return

    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def download_imdb_datasets(
    base_url: str,
    files: Iterable[ImdbFile],
    raw_dir: Path,
) -> list[Path]:
    downloaded: list[Path] = []
    for imdb_file in files:
        url = f"{base_url.rstrip('/')}/{imdb_file.name}"
        dest = raw_dir / imdb_file.name
        download_file(url, dest)
        downloaded.append(dest)
    return downloaded