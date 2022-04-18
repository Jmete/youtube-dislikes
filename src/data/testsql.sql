SELECT id,view_count,like_count,dislike_count FROM video_data LIMIT 5;

\copy (SELECT id,view_count,like_count,dislike_count FROM video_data LIMIT 5) to './data/processed/testsqlcopy5.csv' csv header;