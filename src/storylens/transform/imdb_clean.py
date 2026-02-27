from __future__ import annotations

from pathlib import Path
import pandas as pd


NA_VALUES = ["\\N"]


def read_tsv_gz(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep="\t",
        compression="gzip",
        na_values=NA_VALUES,
        low_memory=False,
    )


def clean_title_basics(df: pd.DataFrame) -> pd.DataFrame:
    # Garder uniquement les films
    df = df[df["titleType"] == "movie"].copy()

    # Colonnes utiles pour StoryLens (cinéma + narration)
    keep_cols = [
        "tconst",
        "primaryTitle",
        "originalTitle",
        "startYear",
        "runtimeMinutes",
        "genres",
    ]
    df = df[keep_cols]

    # Typage
    df["startYear"] = pd.to_numeric(df["startYear"], errors="coerce")
    df["runtimeMinutes"] = pd.to_numeric(df["runtimeMinutes"], errors="coerce")

    # Normalisation noms colonnes
    df.columns = [
        "imdb_id",
        "title",
        "original_title",
        "year",
        "runtime_minutes",
        "genres",
    ]

    return df


def clean_title_ratings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = ["imdb_id", "average_rating", "num_votes"]
    return df