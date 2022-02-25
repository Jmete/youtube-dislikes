## This file is intended to connect to the database, read json files from our storage server,
## load it into pandas, then insert that into the postgres table.

import yaml
import glob
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import psycopg2
import json

config = yaml.safe_load(open('././config.yml'))

host = config["config"]["dbip"]
database = config["config"]["dbname"]
user = config["config"]["dbuser"]
pw = config["config"]["dbpw"]
video_table_name = config["config"]["dbvideotable"]


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

    youtubefilepaths = glob.glob(storagepath + "**/*.gz", recursive=True)
    youtube_len = len(youtubefilepaths)
    print(f"Total files is {youtube_len}")

    # Chunk the json.gz into 400 files at a time for processing. You can change that batch size if you have less memory.
    for yi, ypaths in enumerate(chunks(youtubefilepaths,400)):
        print(f"Beginning Chunk #{yi}")
        youtube201902_df = None
        for i, p in enumerate(ypaths):
            if i == 0:
                youtube201902_df = pd.read_json(p, compression='gzip')
            else:
                youtube201902_df = pd.concat([youtube201902_df, pd.read_json(p, compression='gzip')],axis=0,join='outer')

            if i % 50 == 0:
                print(f"Got {i} files out of {len(ypaths)} in this chunk")


        # Convert dates to timestamp
        youtube201902_df["fetch_date"] = pd.to_datetime(youtube201902_df["fetch_date"], format='%Y%m%d%H%M%S', errors='coerce')
        youtube201902_df["upload_date"] = pd.to_datetime(youtube201902_df["upload_date"], format='%Y%m%d', errors='coerce')

        # convert dict to object that postgres can accept
        cols_to_convert = ['formats','credits','recommended_videos','headline_badges']
        for c in cols_to_convert:
            # youtube201902_df[c] = youtube201902_df[c].apply(psycopg2.extras.Json)
            youtube201902_df[c] = youtube201902_df[c].apply(lambda x: json.dumps(x).replace("NaN", "null"))

        enter_data_video(youtube201902_df)
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
            df.to_sql(video_table_name,con=engine,if_exists='append',index=False)
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