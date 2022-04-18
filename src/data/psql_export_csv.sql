-- These scripts were entered through psql to export csv files for analysis and model training / testing purposes.
-- If there is an issue with these commands, try replacing \copy with COPY
-- Make sure your path to save the processed files is correct. Depending on where you run the file from, you may need to adjust it.

-- SQL Commands through psql are the following:
-- Most disliked: 
\copy (SELECT * FROM video_data ORDER BY dislike_like_ratio DESC LIMIT 500000) to './data/processed/mostliked500k_new.csv' csv header;

-- Most liked: 
\copy (SELECT * FROM video_data ORDER BY dislike_like_ratio ASC LIMIT 500000) to './data/processed/mostliked_500000.csv' csv header;

-- 1% Random Sample:
\copy (SELECT * FROM video_data TABLESAMPLE BERNOULLI (1)) to './data/processed/random_percent_1.csv' csv header;

-- 0.2% Random Sample: 
\copy (SELECT * FROM video_data TABLESAMPLE BERNOULLI (0.2)) to './data/processed/random_percent_point2.csv' csv header;

-- 10% Random Sample: Only used for exploration, not in the final pipeline.
-- \copy (SELECT * FROM video_data TABLESAMPLE BERNOULLI (10)) to './data/processed/random_percent_10.csv' csv header;