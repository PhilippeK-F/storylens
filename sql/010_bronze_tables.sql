CREATE TABLE IF NOT EXISTS bronze_movies (
  imdb_id TEXT PRIMARY KEY,
  title TEXT,
  original_title TEXT,
  year INT,
  runtime_minutes INT,
  genres TEXT,
  average_rating NUMERIC,
  num_votes INT
);