CREATE OR REPLACE VIEW gold_story_signals AS
SELECT
  imdb_id,
  title,
  year,
  runtime_minutes,
  average_rating,
  num_votes,
  genres,

  CASE
    WHEN runtime_minutes IS NULL THEN NULL
    WHEN runtime_minutes < 80 THEN 'Short'
    WHEN runtime_minutes < 100 THEN 'Standard'
    WHEN runtime_minutes < 130 THEN 'Long'
    ELSE 'Epic'
  END AS runtime_bucket,

  CASE
    WHEN num_votes IS NULL THEN NULL
    WHEN num_votes < 1000 THEN 'Low exposure'
    WHEN num_votes < 10000 THEN 'Medium exposure'
    WHEN num_votes < 100000 THEN 'High exposure'
    ELSE 'Mass exposure'
  END AS exposure_bucket,

  (year/10)*10 AS decade
FROM bronze_movies
WHERE year IS NOT NULL AND year >= 1900;