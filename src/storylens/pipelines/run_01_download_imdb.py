from __future__ import annotations

import os
from pathlib import Path

from storylens.extract.imdb_downloader import ImdbFile, download_imdb_datasets


def main() -> None:
    base_url = os.getenv("IMDB_BASE_URL", "https://datasets.imdbws.com")
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    raw_dir = data_dir / "raw" / "imdb"

    files = [
        ImdbFile("title.basics.tsv.gz"),
        ImdbFile("title.ratings.tsv.gz"),
        # Optionnel ensuite :
        # ImdbFile("title.crew.tsv.gz"),
        # ImdbFile("title.principals.tsv.gz"),
        # ImdbFile("name.basics.tsv.gz"),
    ]

    paths = download_imdb_datasets(base_url=base_url, files=files, raw_dir=raw_dir)

    # Petit log utile pour README/portfolio
    for p in paths:
        print(f"Downloaded: {p} ({p.stat().st_size / (1024*1024):.1f} MB)")


if __name__ == "__main__":
    main()