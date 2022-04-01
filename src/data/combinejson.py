import glob
import numpy as np
import pandas as pd
import cudf
import pickle
import yaml
import os

ROOT_DIR = os.path.abspath(os.curdir)
config_path = os.path.join(ROOT_DIR,"config.yml")

config = yaml.safe_load(open(config_path))
storagepath = config["config"]["storepath"]

pathlog_path = os.path.join(ROOT_DIR,"data/interim/pathlog.pickle")
allpaths_path = os.path.join(ROOT_DIR,"data/interim/allpaths.pickle")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst.
        Code from stackoverflow: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def log_paths(paths):
    # Based on code from stackoverflow https://stackoverflow.com/questions/26835477/pickle-load-variable-if-exists-or-create-and-save-it
    try:
        pathlist = pickle.load(open(pathlog_path, "rb"))
        new_paths = paths
        pathlist.extend(new_paths)
        pickle.dump(pathlist, open(pathlog_path, "wb"))
    except (OSError, IOError) as e:
        pathlist = paths
        pickle.dump(pathlist, open(pathlog_path, "wb"))

def get_file_paths(storagepath):
    # Based on code from stackoverflow https://stackoverflow.com/questions/26835477/pickle-load-variable-if-exists-or-create-and-save-it
    try:
        allpaths = pickle.load(open(allpaths_path, "rb"))
    except (OSError, IOError) as e:
        allpaths = sorted(glob.glob(storagepath + "**/*.gz", recursive=True))
        pickle.dump(allpaths, open(allpaths_path, "wb"))
    return allpaths

def combine_json(storagepath):

    youtubefilepaths = get_file_paths(storagepath)
    youtube_len = len(youtubefilepaths)
    chunksize = 500
    print(f"Total files is {youtube_len}")

    # Check for already done chunks based on the parquet file
    try:
        chunksdone = sorted(glob.glob(storagepath + "/parq/*.parquet", recursive=True))
        chunknumbers = [int(x.split("/parq/")[1].split(".")[0]) for x in chunksdone]
        print(f"Chunks done already: {chunknumbers}")
    except:
        chunknumbers = []

    # Chunk the json.gz into 400 files at a time for processing. You can change that batch size if you have less memory.
    for yi, ypaths in enumerate(chunks(youtubefilepaths,chunksize)):

        if yi in chunknumbers:
            print("This chunk is already done. Skipping.")
        else:
            print(f"Beginning Chunk #{yi}")
            youtube201902_df = None
            for i, p in enumerate(ypaths):
                if i == 0:
                    youtube201902_df = pd.read_json(p, compression='gzip')
                else:
                    youtube201902_df = pd.concat([youtube201902_df, pd.read_json(p, compression='gzip')],axis=0,join='outer')

                if i % 50 == 0:
                    print(f"Got {i} files out of {len(ypaths)} in this chunk")

            parq_save_path = f"{storagepath}/parq/{yi}.parquet"
            youtube201902_df.to_parquet(parq_save_path)

            # Log which paths we have already done
            log_paths(ypaths)

def read_parq(storagepath):
    df = cudf.read_parquet(storagepath)
    print(df.head())

if __name__ == "__main__":
    combine_json(storagepath)


