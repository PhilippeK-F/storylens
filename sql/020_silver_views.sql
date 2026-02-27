-- Silver: genres normalisés en table de liaison
CREATE TABLE IF NOT EXISTS silver_movie_genres (
  imdb_id TEXT NOT NULL,
  genre TEXT NOT NULL,
  PRIMARY KEY (imdb_id, genre)
);

-- (Re)build genres table from bronze
TRUNCATE silver_movie_genres;

INSERT INTO silver_movie_genres (imdb_id, genre)
SELECT
  imdb_id,
  TRIM(g) AS genre
FROM bronze_movies
CROSS JOIN LATERAL unnest(string_to_array(genres, ',')) AS g
WHERE genres IS NOT NULL AND genres <> '';

-- Silver view: films enrichis (prêt dashboard)
CREATE OR REPLACE VIEW silver_movies_enriched AS
SELECT
  b.imdb_id,
  b.title,
  b.original_title,
  b.year,
  b.runtime_minutes,
  b.average_rating,
  b.num_votes,
  b.genres
FROM bronze_movies b;