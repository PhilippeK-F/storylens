from __future__ import annotations

from pathlib import Path
import os

from storylens.load.postgres_copy_loader import (
    parquet_to_csv,
    copy_csv_to_postgres,
)


def main() -> None:
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    parquet_path = data_dir / "staging" / "imdb" / "imdb_movies.parquet"
    csv_path = data_dir / "staging" / "imdb" / "imdb_movies.csv"

    print("Converting parquet -> csv...")
    cols = parquet_to_csv(parquet_path, csv_path)

    print("Loading into Postgres (COPY)...")
    copy_csv_to_postgres(csv_path, table="bronze_movies", columns=cols)

    print("Load completed: bronze_movies")


if __name__ == "__main__":
    main()