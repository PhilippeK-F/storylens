StoryLens
End-to-End Data Engineering Project — Cinema Analytics
Project Overview

StoryLens is a production-style Data Engineering project built around large-scale cinema datasets.

The goal is to design a reproducible data pipeline that ingests raw IMDb data, structures it into analytical layers, and exposes business-ready KPIs through a connected dashboard.

----------------------------------------------------------------------------
## QUICKSTART

1. Start PostgreSQL
docker compose up -d postgres
2. Run full data pipeline (download + load + marts)
docker compose run --rm pipeline
3. Launch dashboard
docker compose up dashboard
----------------------------------------------------------------------------


This project demonstrates:

Data ingestion at scale (~739k movies)

Structured data modeling (Bronze / Silver / Gold)

Efficient bulk loading (PostgreSQL COPY)

Analytical SQL view design

Dashboard data serving layer

Architecture
Data Flow

IMDb raw datasets (TSV.gz)
→ Python extraction
→ Parquet staging
→ PostgreSQL Bronze layer
→ Silver normalization
→ Gold analytical marts
→ Streamlit dashboard

Data Volume

~738,973 movies

~1,013,553 genre relationships

Multi-decade coverage (1900–present)

Tech Stack

Backend:

Python 3.11

Pandas

Psycopg (PostgreSQL driver)

SQLAlchemy

Database:

PostgreSQL 16 (Docker)

Serving:

Streamlit

Infrastructure:

Docker Compose

Virtual environments

Data Modeling Strategy
Bronze Layer — Raw Structured Data

Table: bronze_movies

Cleaned IMDb movie data

Ratings and vote counts integrated

Optimized loading via COPY

Primary key: imdb_id

Purpose:
Structured storage of curated raw data ready for transformation.

Silver Layer — Normalization

Table: silver_movie_genres

Many-to-many genre normalization

Split of comma-separated genre fields

Clean relational model

Purpose:
Enable analytical grouping and aggregation.

Gold Layer — Analytical Views

Views:

gold_top_movies

gold_genre_kpis

gold_decade_kpis

gold_story_signals

Purpose:
Business-oriented data marts optimized for dashboard consumption.

Example Analytical Outputs

Average rating by genre

Runtime evolution across decades

Popularity vs perceived quality

Narrative pacing proxy (runtime buckets)

Exposure segmentation (vote-based tiers)

Performance Considerations

Bulk loading via PostgreSQL COPY (no row-by-row inserts)

Parquet staging format

Layer separation for scalability

SQL-based aggregation for BI readiness

----------------------------------------------------------------------------

Running the Project :

## Setup :
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

## Start Database :
docker compose up -d

## Execute Pipeline :
python -m storylens.pipelines.run_01_download_imdb
python -m storylens.pipelines.run_02_stage_imdb
python -m storylens.pipelines.run_03_load_bronze

## Build Analytical Layers :
Get-Content sql/020_silver_views.sql | docker exec -i projet_storylens-postgres-1 psql -U warehouse -d warehouse
Get-Content sql/030_gold_marts.sql | docker exec -i projet_storylens-postgres-1 psql -U warehouse -d warehouse
Get-Content sql/040_gold_story_signals.sql | docker exec -i projet_storylens-postgres-1 psql -U warehouse -d warehouse

Launch Dashboard :
python -m streamlit run dashboard/streamlit_app.py

----------------------------------------------------------------------------

## Architecture Diagram

```mermaid
flowchart LR

    A[IMDb Datasets<br>TSV.GZ Files] --> B[Python Extract Layer]
    B --> C[Parquet Staging]
    C --> D[PostgreSQL Bronze]
    D --> E[Silver Normalization]
    E --> F[Gold Analytical Views]
    F --> G[Streamlit Dashboard]

    subgraph Data Engineering Pipeline
        B
        C
        D
        E
        F
    end
