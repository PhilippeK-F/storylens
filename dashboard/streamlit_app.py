import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title="StoryLens", layout="wide")
st.title("StoryLens — Cinema KPIs")

host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "warehouse")
user = os.getenv("POSTGRES_USER", "warehouse")
pwd = os.getenv("POSTGRES_PASSWORD", "warehouse")

engine = create_engine(f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}")

@st.cache_data(ttl=300)
def load_df(sql: str) -> pd.DataFrame:
    return pd.read_sql(text(sql), engine)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Genre KPIs", "Decade KPIs", "Top Movies", "Scenario Signals"])

with tab1:
    st.subheader("KPIs by Genre")
    df = load_df("SELECT * FROM gold_genre_kpis")
    st.dataframe(df, use_container_width=True)

    metric = st.selectbox("Chart metric", ["total_votes", "movies_count", "avg_rating", "avg_runtime"])
    chart_df = df[["genre", metric]].set_index("genre").sort_values(metric, ascending=False).head(20)
    st.bar_chart(chart_df)

with tab2:
    st.subheader("KPIs by Decade")
    df = load_df("SELECT * FROM gold_decade_kpis")
    st.dataframe(df, use_container_width=True)

    st.line_chart(df.set_index("decade")[["avg_rating"]])
    st.line_chart(df.set_index("decade")[["avg_runtime"]])

with tab3:
    st.subheader("Top Movies (filter by minimum votes)")
    min_votes = st.slider("Minimum votes", 0, 500000, 50000, 25000)

    sql = f"""
    SELECT imdb_id, title, year, runtime_minutes, average_rating, num_votes, genres
    FROM bronze_movies
    WHERE num_votes IS NOT NULL AND num_votes >= {min_votes}
    ORDER BY average_rating DESC, num_votes DESC
    LIMIT 200;
    """
    df = load_df(sql)
    st.dataframe(df, use_container_width=True)
    
with tab4:
    st.subheader("Scenario Signals (proxies based on IMDb data)")

    df = load_df("""
        SELECT decade, runtime_bucket, exposure_bucket, average_rating, num_votes, runtime_minutes
        FROM gold_story_signals
        WHERE average_rating IS NOT NULL
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Average rating by runtime bucket")
        agg = (
            df.groupby("runtime_bucket", dropna=True)["average_rating"]
            .mean()
            .sort_values(ascending=False)
            .to_frame("avg_rating")
        )
        st.bar_chart(agg)

    with col2:
        st.caption("Average rating by exposure bucket (votes)")
        agg = (
            df.groupby("exposure_bucket", dropna=True)["average_rating"]
            .mean()
            .to_frame("avg_rating")
        )
        st.bar_chart(agg)

    st.divider()

    st.caption("Runtime vs Rating (sample)")
    sample_n = st.slider("Sample size", 2000, 50000, 10000, 2000)
    df_scatter = load_df(f"""
        SELECT runtime_minutes, average_rating, num_votes, decade
        FROM gold_story_signals
        WHERE runtime_minutes IS NOT NULL AND average_rating IS NOT NULL
        ORDER BY num_votes DESC NULLS LAST
        LIMIT {sample_n}
    """)
    st.scatter_chart(df_scatter, x="runtime_minutes", y="average_rating")

    st.divider()

    st.caption("Decade trends (rating and runtime)")
    df_dec = load_df("""
        SELECT decade,
               AVG(average_rating) AS avg_rating,
               AVG(runtime_minutes) AS avg_runtime,
               SUM(num_votes) AS total_votes
        FROM gold_story_signals
        WHERE runtime_minutes IS NOT NULL AND average_rating IS NOT NULL
        GROUP BY decade
        ORDER BY decade
    """)
    st.line_chart(df_dec.set_index("decade")[["avg_rating"]])
    st.line_chart(df_dec.set_index("decade")[["avg_runtime"]])
    
    st.divider()
    st.subheader("Runtime distribution by genre (proxy for narrative pacing)")

    df_rt = load_df("""
        SELECT g.genre, b.runtime_minutes
        FROM silver_movie_genres g
        JOIN bronze_movies b USING (imdb_id)
        WHERE b.runtime_minutes IS NOT NULL
          AND b.year IS NOT NULL AND b.year >= 1900
    """)

    top_genres = (
        df_rt["genre"].value_counts().head(15).index.tolist()
    )
    df_rt = df_rt[df_rt["genre"].isin(top_genres)]

    # Median runtime by genre (more robust than mean)
    df_med = (
        df_rt.groupby("genre")["runtime_minutes"]
        .median()
        .sort_values(ascending=False)
        .to_frame("median_runtime")
    )
    st.bar_chart(df_med)
    
    st.divider()
    st.subheader("Quality vs Popularity")

    # Filtres simples
    decades = load_df("SELECT DISTINCT decade FROM gold_story_signals ORDER BY decade")["decade"].dropna().tolist()
    decade = st.selectbox("Decade", decades, index=len(decades)-1)

    genres = load_df("SELECT DISTINCT genre FROM silver_movie_genres ORDER BY genre")["genre"].tolist()
    genre = st.selectbox("Genre", ["All"] + genres, index=0)

    min_votes = st.slider("Minimum votes", 0, 500000, 10000, 10000)

    if genre == "All":
        sql = f"""
            SELECT b.runtime_minutes, b.average_rating, b.num_votes
            FROM bronze_movies b
            WHERE b.year IS NOT NULL
              AND (b.year/10)*10 = {int(decade)}
              AND b.average_rating IS NOT NULL
              AND b.runtime_minutes IS NOT NULL
              AND b.num_votes IS NOT NULL
              AND b.num_votes >= {int(min_votes)}
            ORDER BY b.num_votes DESC
            LIMIT 20000
        """
    else:
        sql = f"""
            SELECT b.runtime_minutes, b.average_rating, b.num_votes
            FROM bronze_movies b
            JOIN silver_movie_genres g USING (imdb_id)
            WHERE g.genre = '{genre}'
              AND b.year IS NOT NULL
              AND (b.year/10)*10 = {int(decade)}
              AND b.average_rating IS NOT NULL
              AND b.runtime_minutes IS NOT NULL
              AND b.num_votes IS NOT NULL
              AND b.num_votes >= {int(min_votes)}
            ORDER BY b.num_votes DESC
            LIMIT 20000
        """

    df_qp = load_df(sql)

    # Utilise un scatter avec un échantillon si besoin
    st.scatter_chart(df_qp, x="num_votes", y="average_rating")
    st.caption("Interpretation: votes ≈ exposure/popularity, rating ≈ perceived quality.")