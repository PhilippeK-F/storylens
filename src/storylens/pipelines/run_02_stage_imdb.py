from __future__ import annotations

from pathlib import Path
import os
import pandas as pd

from storylens.transform.imdb_clean import (
    read_tsv_gz,
    clean_title_basics,
    clean_title_ratings,
)


def main() -> None:
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    raw_dir = data_dir / "raw" / "imdb"
    staging_dir = data_dir / "staging" / "imdb"
    staging_dir.mkdir(parents=True, exist_ok=True)

    basics_path = raw_dir / "title.basics.tsv.gz"
    ratings_path = raw_dir / "title.ratings.tsv.gz"

    print("Reading basics...")
    basics_raw = read_tsv_gz(basics_path)
    basics = clean_title_basics(basics_raw)

    print("Reading ratings...")
    ratings_raw = read_tsv_gz(ratings_path)
    ratings = clean_title_ratings(ratings_raw)

    print("Joining...")
    movies = basics.merge(ratings, on="imdb_id", how="left")

    # Sauvegarde staging (parquet = rapide, pro)
    out_path = staging_dir / "imdb_movies.parquet"
    movies.to_parquet(out_path, index=False)

    print(f"Staging file written: {out_path}")
    print(f"Rows: {len(movies):,}")


if __name__ == "__main__":
    main()