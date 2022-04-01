## This file is intended to connect to the database, read parquet files from our storage server,
## load it into pandas, then insert that into the postgres table.

import yaml
import glob
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import psycopg2
import json
import pickle
from tqdm import tqdm
from psycopg2.extensions import register_adapter, AsIs
from datetime import datetime
import os

ROOT_DIR = os.path.abspath(os.curdir)
config_path = os.path.join(ROOT_DIR,"config.yml")
config = yaml.safe_load(open(config_path))

host = config["config"]["dbip"]
database = config["config"]["dbname"]
user = config["config"]["dbuser"]
pw = config["config"]["dbpw"]
video_table_name = config["config"]["dbvideotable"]


db_col_names = [
    "id",
    "fetch_date",
    "uploader",
    "uploader_id",
    "upload_date",
    "title",
    "desc_text",
    "category",
    "tags",
    "duration",
    "age_limit",
    "view_count",
    "like_count",
    "dislike_count",
    "average_rating",
    "allow_embed",
    "is_crawlable",
    "allow_sub_contrib",
    "is_live_content",
    "is_ads_enabled",
    "is_comments_enabled",
    "formats",
    "credits",
    "regions_allowed",
    "recommended_videos",
    "headline_badges",
    "unavailable_message",
    "license",
    "view_like_ratio",
    "view_dislike_ratio",
    "like_dislike_ratio",
]

insertedlog_path = os.path.join(ROOT_DIR,"data/interim/insertedlog.pickle")

def log_paths(paths):
    # Based on code from stackoverflow https://stackoverflow.com/questions/26835477/pickle-load-variable-if-exists-or-create-and-save-it
    try:
        pathlist = pickle.load(open(insertedlog_path, "rb"))
        new_paths = paths
        pathlist.extend(new_paths)
        pickle.dump(pathlist, open(insertedlog_path, "wb"))
    except (OSError, IOError) as e:
        pathlist = paths
        pickle.dump(pathlist, open(insertedlog_path, "wb"))

def chunks(lst, n):
    """Yield successive n-sized chunks from lst.
        Code from stackoverflow: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_data_video():

    # Open database connection session
    engine = create_engine(f'postgresql+psycopg2://{user}:{pw}@{host}:5432/{database}')

    storagepath = config["config"]["storepath"]

    youtubefilepaths = sorted(glob.glob(storagepath + "parq/*.parquet", recursive=True))
    youtube_len = len(youtubefilepaths)
    print(f"Total files is {youtube_len}")

    try:
        insertedlog = pickle.load(open(insertedlog_path, "rb"))
        print(insertedlog)
    except:
        insertedlog = []

    for yi, ypaths in enumerate(tqdm(youtubefilepaths)):

        thetime = datetime.now().strftime("%H:%M:%S")
        print(f"Time is: {thetime}")

        if ypaths not in insertedlog:
            youtube201902_df = None
            youtube201902_df = pd.read_parquet(ypaths)
            print(f"Loaded data from {ypaths} into dataframe")

            # Convert dates to timestamp
            youtube201902_df["fetch_date"] = pd.to_datetime(youtube201902_df["fetch_date"], format='%Y%m%d%H%M%S', errors='coerce')
            youtube201902_df["upload_date"] = pd.to_datetime(youtube201902_df["upload_date"], format='%Y%m%d', errors='coerce')

            # convert dict to object that postgres can accept
            cols_to_convert_json = ['formats','credits','recommended_videos','headline_badges']
            cols_to_convert_list = ["tags","regions_allowed"]

            def dump_json(row):
                try:
                    return json.dumps(row.tolist())
                except:
                    return None

            def convert_list(row):
                try:
                    return list(row)
                except:
                    return None

            for c in cols_to_convert_json:
                youtube201902_df[c] = youtube201902_df[c].apply(dump_json)

            for c in cols_to_convert_list:
                youtube201902_df[c] = youtube201902_df[c].apply(convert_list)
            
            youtube201902_df["view_like_ratio"] = youtube201902_df["view_count"] / youtube201902_df["like_count"]
            youtube201902_df["view_dislike_ratio"] = youtube201902_df["view_count"] / youtube201902_df["dislike_count"]
            youtube201902_df["like_dislike_ratio"] = youtube201902_df["like_count"] / youtube201902_df["dislike_count"]

            # Drop inf rows
            youtube201902_df = youtube201902_df[youtube201902_df["like_dislike_ratio"]!= np.inf]
            
            # Drop NA values
            youtube201902_df = youtube201902_df.dropna(subset=["like_dislike_ratio"])

            # Rename description column to match database table
            youtube201902_df = youtube201902_df.rename(columns={"description":"desc_text"})

            # Order columns as per the database schema
            youtube201902_df = youtube201902_df[db_col_names]

            # Enter data into database and log the paths completed
            enter_data_video(youtube201902_df)
            log_paths([ypaths])
            del youtube201902_df
        else:
            print(f"{ypaths} already inserted. Skipping.")

    print("Data entry process completed")


def enter_data_video(df):
    
    # # Get data
    # df = get_data_video()

    # Get database connection engine
    # print("Creating Engine...")
    engine = create_engine(f'postgresql://{user}:{pw}@{host}:5432/{database}')
    print("Created Engine")

    # Open session and write data to database
    print("Attempting to write to DB...")
    with Session(engine) as session:
        try:
            df.to_sql(video_table_name,con=engine,if_exists='append',index=False,method='multi',chunksize=10000)
        except Exception as e:
            print("Error writing to DB")
            print("Error is:")
            print(e)

    print("Finished writing to DB")

if __name__ == "__main__":
    verify_video = input("""Type 'yes' if you want to enter video data to database: """)
    if verify_video.lower() == "yes":
        print("Beginning video data entry.")
        get_data_video()
    else:
        print("Skipping video data entry.")
    
    ### TODO: Function to enter video comment data to comment table.