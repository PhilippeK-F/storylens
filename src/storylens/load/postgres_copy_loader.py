from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import pandas as pd
import psycopg


@dataclass(frozen=True)
class PgConfig:
    host: str
    port: int
    db: str
    user: str
    password: str


def get_pg_config() -> PgConfig:
    return PgConfig(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        db=os.getenv("POSTGRES_DB", "warehouse"),
        user=os.getenv("POSTGRES_USER", "warehouse"),
        password=os.getenv("POSTGRES_PASSWORD", "warehouse"),
    )


def parquet_to_csv(parquet_path: Path, csv_out: Path) -> list[str]:
    df = pd.read_parquet(parquet_path)

    # Force proper integer types (nullable) so CSV doesn't contain "1894.0"
    int_cols = ["year", "runtime_minutes", "num_votes"]
    for c in int_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    # rating can stay float/decimal
    if "average_rating" in df.columns:
        df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce")

    # Keep NULLs as empty values; COPY will parse empty as NULL by default
    df = df.where(pd.notnull(df), None)

    csv_out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_out, index=False)

    return list(df.columns)


def copy_csv_to_postgres(csv_path: Path, table: str, columns: list[str]) -> None:
    cfg = get_pg_config()
    col_list = ", ".join([f'"{c}"' for c in columns])

    copy_sql = f"""
        COPY {table} ({col_list})
        FROM STDIN WITH (FORMAT csv, HEADER true)
    """

    # Explicit connect to avoid VS Code type checker confusion
    conn = psycopg.connect(
        host=cfg.host,
        port=cfg.port,
        dbname=cfg.db,
        user=cfg.user,
        password=cfg.password,
    )
    try:
        with conn:
            with conn.cursor() as cur:
                with csv_path.open("r", encoding="utf-8") as f:
                    with cur.copy(copy_sql) as copy:
                        for line in f:
                            copy.write(line)
    finally:
        conn.close()