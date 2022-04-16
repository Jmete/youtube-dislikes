import pandas as pd
from cdownload_noargs import main
import os
from tqdm import tqdm
import sys


# VIDEO_DATA_PATH = './data/'

def run_script(start_from, should_convert_to_text_file,csv_filename):
    """
    This function will download comments for videos in the given csv file
    
    Args:
        start_from (int):   
            The position of the video id in the csv. Because the program
            will create a text file from the video ids in the csv, the position will be index + 1

        should_convert_to_text_file (bool): 
            If True, the program will open the csv and extract all the video ids.
            The program expects the csv file to exist in the same place as this 
            python script.
            
            Ideally, this should be set to True only the first time. Once the txt file is created
            the program can then use the txt file to get the video ids. Loading data from a text file
            which contains only the video ids is faster than loading the csv file everytime the script runs. 
    
    How this script works:
        1.  The function will first open the csv file from the path provided
            and extract all the video ids and store it in a list. This is done to speed up the reading 
            of the video ids incase the script is stopped midway. Ideally this should happen only once
        
        2.  Once the video ids are retrieved, the final_df DataFrame will be created. This DatFrame will
            hold the comments for each video. The final_df will be created only once. If the dataframe is found 
            in the path provided, the program will continue to append the new data to the existing DataFrame.
            To ensure that no data is lost, every time the script is run, the program will create a new file
            as follows: filename_comments_{start_from}.csv. Hence the data that existed before this will 
            not be touched and can finally be merged togather.
        
        3.  The loop to download the comments will start. Here the start_from argument is needed. When running
            the program for the first time, start_from should be 0. Otherwise start_from will be equal to the 
            index position + 1 of the video id to begin from. For example, if the first time the program extracts comments
            for 10 videos after which it is stopped, when running the second time, start_from will be equal to 11 
            or the 11th video from the txt file created in step 1.
        
        4.  Every 100th iteration, the program will save the data to the dataframe created in Step 2. 
        
        5.  The program can be stopped at any time. When a KeyboardInterrupt is detected, the program will save
            the current progress to the dataframe created in step 2. The next time the code is run, the position of
            the next video id can be provided. 
        
        6.  Incase ther is a network error, the program will gracefully save the extracted data to the drive, and end
            the process.
            
        7.  This script will also save the json files of all the comments in COMMENTS_DOWNLOAD_PATH location. 
            These json files can be used as a fail safe incase the dataframe gets corrupted. 
    """

    ROOT_DIR = os.path.abspath(os.curdir)
    ORIGINAL_CSV_PATH = os.path.join(ROOT_DIR,f"data/processed/{csv_filename}.csv")
    VIDEO_IDS_LIST_PATH = os.path.join(ROOT_DIR,f"data/interim/video_ids_{csv_filename}.txt")
    COMMENTS_DOWNLOAD_PATH = os.path.join(ROOT_DIR,f"data/processed/comments_json/{csv_filename}")
    COMMENTS_DOWNLOAD_PATH_CSV = os.path.join(ROOT_DIR,f"data/processed/comments_csv/")


    if (should_convert_to_text_file == 'y') or (should_convert_to_text_file == 'yes'):
        print(f"Opening {csv_filename}.csv")
        df = pd.read_csv(ORIGINAL_CSV_PATH)['id']
        
        with open(VIDEO_IDS_LIST_PATH, 'w') as file:
            for id in list(df):
                file.write(f"{id}\n")
        print("text file created. This file will be used in the future for downloading comments")
    
    # create the COMMENTS_DOWNLOAD_PATH folder. This will hold all the json files
    os.makedirs(COMMENTS_DOWNLOAD_PATH, exist_ok=True)

    # create the COMMENTS_DOWNLOAD_PATH folder. This will hold all the json files
    os.makedirs(COMMENTS_DOWNLOAD_PATH_CSV, exist_ok=True)
    
    comments_file_name = f'{csv_filename}_videos_comments_{start_from}.csv'
    COMMENT_FILE_PATH = os.path.join(COMMENTS_DOWNLOAD_PATH_CSV,comments_file_name)

    print("checking for final_df")
    if comments_file_name in os.listdir(COMMENTS_DOWNLOAD_PATH_CSV):
        final_df = pd.read_csv(COMMENT_FILE_PATH, lineterminator='\n', low_memory=False)
    else:
        print("final_df does not exist. Creating the dataframe now.")
        cols = ['cid', 'text', 'time', 'author', 'channel', 'votes', 'photo', 'heart', 'video_id']
        final_df = pd.DataFrame(columns=cols)

    with open(VIDEO_IDS_LIST_PATH) as file:
        all_video_ids = [x.strip() for x in file.readlines()] # get all the video_ids as a list

    count = 0
    print('Starting the loop')
    for video_id in tqdm(all_video_ids[start_from:], initial=start_from, total=len(all_video_ids)):
        try:
            output_file = f'{COMMENTS_DOWNLOAD_PATH}/comments_{video_id}.json'
            main(video_id, output_file, sort_by=0, limit=10)
            
            df = pd.read_json(output_file, lines=True)
            final_df = pd.concat([final_df, df])

            if count == 100:
                print('--------------------------------------')
                print('Saving to drive')
                print('--------------------------------------')
                final_df.to_csv(COMMENT_FILE_PATH, index=False)
                count = 0

            del df
            count += 1
        
        except KeyboardInterrupt:
            print("Received KeyboardInterrupt. Saving current instance to drive.")
            print(f"The latest video id processed was {video_id}")
            print(f"The latest video id in final_df is {final_df.iloc[-1, -1]}")
            
            final_df.to_csv(COMMENT_FILE_PATH, index=False)
            break
            
        except ConnectionError:
            print("There seems to be a connection issue. Saving current instance to drive.")
            print(f"The latest video id processed was {video_id}")
            print(f"The latest video id in final_df is {final_df.iloc[-1, -1]}")
            
            final_df.to_csv(COMMENT_FILE_PATH, index=False)
            break
        
    final_df.to_csv(COMMENT_FILE_PATH, index=False)

if __name__ == "__main__":
    
    start_from, should_convert_to_text_file, csv_filename = None, None, None
    
    try:
        start_from = sys.argv[1]
    except IndexError:
        msg = """
        start_from argument required. 
        When running the program for the first time, start_from should be 0. 
        Otherwise start_from will be equal to the index position + 1 of the video id to begin from
        """
        print(msg)
    
    try:
        should_convert_to_text_file = sys.argv[2]
    except IndexError:
        msg = """
        should_convert_to_text_file argument required. 
        When running the program for the first time, should_convert_to_text_file should be True.
        This argument ensures that the txt file is created from the csv. 
        """
        print(msg)

    try:
        csv_filename = sys.argv[3]
    except IndexError:
        msg = """
        csv_filename required.
        """
        print(msg)
        
    if start_from and should_convert_to_text_file and csv_filename:
        run_script(int(start_from), should_convert_to_text_file,str(csv_filename).split(".")[0])
    else:
        print("Error in args. Please try again.")