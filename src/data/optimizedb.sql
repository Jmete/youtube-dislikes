-- This script performs optimizations on the database to improve performance.
-- Doing so allowed us to shorten processing times from over 8 hours to a few minutes or even seconds depending on the complexity of the sql command.
-- Note: We entered these commands through psql

ANALYZE video_data;

CREATE INDEX idx_views ON video_data(view_count);

CREATE INDEX idx_likes ON video_data(like_count);

CREATE INDEX idx_dislikes ON video_data(dislike_count);

CREATE INDEX idx_dislike_like_ratio ON video_data(dislike_like_ratio);


-- It should be noted that during the creation of the database table, 
-- we will naturally have an index already on the unique id of the row as 
-- well as the video_id being designated as a unique column. 
-- The final indexes should be the following:
-- - "video_data_pkey" PRIMARY KEY, btree (row_id)
-- - "idx_dislike_like_ratio" btree (dislike_like_ratio)
-- - "idx_dislikes" btree (dislike_count)
-- - "idx_likes" btree (like_count)
-- - "idx_views" btree (view_count)
-- - "video_data_id_key" UNIQUE CONSTRAINT, btree (id)