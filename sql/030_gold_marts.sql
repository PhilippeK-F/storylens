CREATE OR REPLACE VIEW gold_top_movies AS
SELECT
  imdb_id,
  title,
  year,
  runtime_minutes,
  average_rating,
  num_votes,
  genres
FROM bronze_movies
WHERE num_votes IS NOT NULL AND num_votes >= 50000
ORDER BY average_rating DESC, num_votes DESC;

CREATE OR REPLACE VIEW gold_genre_kpis AS
SELECT
  g.genre,
  COUNT(*) AS movies_count,
  AVG(b.average_rating) AS avg_rating,
  AVG(b.runtime_minutes) AS avg_runtime,
  SUM(b.num_votes) AS total_votes
FROM silver_movie_genres g
JOIN bronze_movies b USING (imdb_id)
WHERE b.average_rating IS NOT NULL
GROUP BY g.genre
ORDER BY total_votes DESC;

CREATE OR REPLACE VIEW gold_decade_kpis AS
SELECT
  (year/10)*10 AS decade,
  COUNT(*) AS movies_count,
  AVG(average_rating) AS avg_rating,
  AVG(runtime_minutes) AS avg_runtime,
  SUM(num_votes) AS total_votes
FROM bronze_movies
WHERE year IS NOT NULL AND year >= 1900
GROUP BY decade
ORDER BY decade;