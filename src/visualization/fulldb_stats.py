import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import psycopg2
import os
import yaml

ROOT_DIR = os.path.abspath(os.curdir)
config_path = os.path.join(ROOT_DIR,"config.yml")
config = yaml.safe_load(open(config_path))

host = config["config"]["dbip"]
database = config["config"]["dbname"]
user = config["config"]["dbuser"]
pw = config["config"]["dbpw"]
video_table_name = config["config"]["dbvideotable"]

save_stats_path = os.path.join(ROOT_DIR,"data/interim/fulldb_stats.pickle")
save_stats_grouped_path = os.path.join(ROOT_DIR,"data/interim/fulldb_stats_grouped.pickle")

def get_stats_sql():

    # Open database connection session
    engine = create_engine(f'postgresql+psycopg2://{user}:{pw}@{host}:5432/{database}')

    query_standard_stats = """
    SELECT COUNT(*) AS row_count, 
    MIN(view_count) AS view_count_min,
    MAX(view_count) AS view_count_max,
    AVG(view_count) AS view_count_avg,
    MIN(like_count) AS like_count_min,
    MAX(like_count) AS like_count_max,
    AVG(like_count) AS like_count_avg,
    MIN(dislike_count) AS dislike_count_min,
    MAX(dislike_count) AS dislike_count_max,
    AVG(dislike_count) AS dislike_count_avg,
    MIN(average_rating) AS average_rating_min,
    MAX(average_rating) AS average_rating_max,
    AVG(average_rating) AS average_rating_avg,
    MIN(dislike_like_ratio) AS dislike_like_ratio_min,
    MAX(dislike_like_ratio) AS dislike_like_ratio_max,
    AVG(dislike_like_ratio) AS dislike_like_ratio_avg
    FROM video_data;
    """

    query_standard_stats_group_by_category = """
    SELECT category,
    COUNT(*) AS row_count, 
    MIN(view_count) AS view_count_min,
    MAX(view_count) AS view_count_max,
    AVG(view_count) AS view_count_avg,
    MIN(like_count) AS like_count_min,
    MAX(like_count) AS like_count_max,
    AVG(like_count) AS like_count_avg,
    MIN(dislike_count) AS dislike_count_min,
    MAX(dislike_count) AS dislike_count_max,
    AVG(dislike_count) AS dislike_count_avg,
    MIN(average_rating) AS average_rating_min,
    MAX(average_rating) AS average_rating_max,
    AVG(average_rating) AS average_rating_avg,
    MIN(dislike_like_ratio) AS dislike_like_ratio_min,
    MAX(dislike_like_ratio) AS dislike_like_ratio_max,
    AVG(dislike_like_ratio) AS dislike_like_ratio_avg
    FROM video_data
    GROUP BY category;
    """
    # Open session and read data
    print("Attempting to read DB...")
    with Session(engine) as session:
        try:
            print("Reading standard stats")
            stats_df = pd.read_sql(query_standard_stats,con=engine)
            print(stats_df)
            stats_df.to_pickle(save_stats_path)
            print("Saved standard stats")
        except Exception as e:
            print("Error reading DB")
            print("Error is:")
            print(e)

        try:
            print("Reading stats grouped by category")
            stats_grouped_df = pd.read_sql(query_standard_stats_group_by_category,con=engine)
            print(stats_grouped_df)
            stats_grouped_df.to_pickle(save_stats_grouped_path)
            print("Saved grouped by category")
        except Exception as e:
            print("Error reading DB")
            print("Error is:")
            print(e)

if __name__ == "__main__":
    print("Starting script to generate basic statistics on dataset")
    get_stats_sql()
