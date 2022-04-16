# This script takes in our csv files that were exported as a training and test set from our main dataset from our database.
# It processes the data and prepares it for model training including type casting, handling NaN or null values, and sentiment analysis features.
# It will also process comment data that was scraped, perform sentiment analysis on them, and join them with the main dataset as extra features.

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path

# Vader for sentiment analysis
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

ROOT_DIR = os.path.abspath(os.curdir)

# Video info csvs. 500K most liked, 500K most disliked, and a 1% random sample.
mostliked=os.path.join(ROOT_DIR,"data/processed/mostliked_500000.csv")
mostdisliked=os.path.join(ROOT_DIR,"data/processed/mostdisliked_500000.csv")
randompct=os.path.join(ROOT_DIR,"data/processed/random_percent_1.csv")

# Separate 0.2% export to use as a test set
randompctpoint2=os.path.join(ROOT_DIR,"data/processed/random_percent_point2.csv")

# Comment csv files
comments_liked_path =  os.path.join(ROOT_DIR, "data/processed/comments_csv/liked_videos_comments_0.csv")
comments_disliked_path = os.path.join(ROOT_DIR,"data/processed/comments_csv/disliked_videos_comments_0.csv")
comments_randompoint2_path = os.path.join(ROOT_DIR,"data/processed/comments_csv/randompercentpoint2_videos_comments_0.csv")

# Randompct1 comment csv files were split into smaller files and processed in parallel to improve scraping time.
# We can get all the paths via regex glob and then concat using list comprehension.
random_csv_paths = sorted(Path(os.path.join(ROOT_DIR,"data/processed/comments_csv")).rglob("randompct1*.csv"))

# Pickle save paths
training_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/training_df.pkl")
testing_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/testing_df.pkl")

# Category codes from the Youtube API
cat_code_dict = {1: 'Film & Animation',
 2: 'Autos & Vehicles',
 10: 'Music',
 15: 'Pets & Animals',
 17: 'Sports',
 18: 'Short Movies',
 19: 'Travel & Events',
 20: 'Gaming',
 21: 'Videoblogging',
 22: 'People & Blogs',
 23: 'Comedy',
 24: 'Entertainment',
 25: 'News & Politics',
 26: 'Howto & Style',
 27: 'Education',
 28: 'Science & Technology',
 29: 'Nonprofits & Activism',
 30: 'Movies',
 31: 'Anime/Animation',
 32: 'Action/Adventure',
 33: 'Classics',
 34: 'Comedy',
 35: 'Documentary',
 36: 'Drama',
 37: 'Family',
 38: 'Foreign',
 39: 'Horror',
 40: 'Sci-Fi/Fantasy',
 41: 'Thriller',
 42: 'Shorts',
 43: 'Shows',
 44: 'Trailers'}

inv_cat_code_dict = {v: k for k, v in cat_code_dict.items()}

def get_main_dfs():
    """
    Transforms csv files of main video data into dataframes ready for processing.

    returns:
        df, df - a dataframe representing the training data and final testing data
    """
    print("Getting dataframes...")
    # Load data into dataframes
    liked=pd.read_csv(mostliked,engine="python")
    disliked=pd.read_csv(mostdisliked,engine="python")
    randompct_df = pd.read_csv(randompct,engine="python")

    # Combine liked, disliked, and random 1% into one df
    combined_df = pd.concat([liked,disliked,randompct_df])
    
    # Shuffle combined df
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)

    # Load 0.2% random sample for final testing of models
    randompctpoint2_df = pd.read_csv(randompctpoint2,engine="python")

    # Load comments df
    comments_liked_df = pd.read_csv(comments_liked_path,lineterminator='\n')
    comments_disliked_df = pd.read_csv(comments_disliked_path,lineterminator='\n')
    comments_random_df = pd.concat([pd.read_csv(r_csv,lineterminator='\n') for r_csv in random_csv_paths],ignore_index=True)

    comments_train=pd.concat([comments_liked_df,comments_disliked_df,comments_random_df],ignore_index=True)

    comments_test = pd.read_csv(comments_randompoint2_path,lineterminator='\n')

    print("Dataframes loaded")

    return combined_df, randompctpoint2_df, comments_train, comments_test

def find_english(df,only_eng=True):
    """
    Takes in a dataframe, performs vader sentiment analysis on it and outputs sentiment, and filters for english only.
    """
    df['desc_text'] = df['desc_text'].str.lower()                                                 #Remove capitalization                                            
    df['desc_text'] = df['desc_text'].str.replace('[^\w\s]','')                                   #Removes extra whitespaces
    df['desc_text'] = df['desc_text'].str.replace('@[A-Za-z0-9]+', '')                            #Removes any tags using @
    df['desc_text'] = df['desc_text'].str.replace('\n', '')                                       #Remove newline 

    data=pd.DataFrame((df.desc_text)).astype(str)
    data['scores']=data['desc_text'].apply(SentimentIntensityAnalyzer().polarity_scores)          #Apply Vader Sentiment Analysis

    data['desc_neu']=data['scores'].apply(lambda score_dict: score_dict['neu'])                        #Extract Neutral Values from dictionary
    data['desc_neg']=data['scores'].apply(lambda score_dict: score_dict['neg'])                        #Extract Negative Values from dictionary
    data['desc_pos']=data['scores'].apply(lambda score_dict: score_dict['pos'])                        #Extract Positive Values from dictionary
    data['desc_compound']=data['scores'].apply(lambda score_dict: score_dict['compound'])              #Extract Compound Values from dictionary

    combined_data=pd.concat([df,data], axis=1).reindex(df.index)                    #Add values back to original dataframe

    # If only eng is true, filter for only english, else return all the data
    if only_eng:
        eng_data= combined_data[combined_data['desc_neu'] != 1]                              #Filter out df values with a neu score of 1 (indicate foreign desc)
        return eng_data
    else:
        return combined_data


def clean_comments(df):
    """
    Takes in comment dataframe and cleans necessary columns and prepares them for sentiment analysis.
    """
    
    df_clean=df[['video_id','votes','text']].copy()                                                #Select necessary columns
    df_clean['text_cleaned'] = df_clean['text'].str.replace('[^\w\s]','')                    #Removes extra whitespaces
    df_clean['text_cleaned'] = df_clean['text_cleaned'].str.replace('@[A-Za-z0-9]+', '')     #Removes any tags using @
    df_clean['text_cleaned'] = df_clean['text_cleaned'].str.replace('\n', '')                #Remove newline punctuation 
    df_clean['text_cleaned'] = df_clean['text_cleaned'].str.lower()                          #Removes Capitalization             

    return df_clean


def comment_sentiment(df_clean):
    """
    Takes in cleaned comment dataframe and performs sentiment analysis on it.
    Groups by video_id using mean and returns the dataframe.
    """
    
    #Designate Sentiment Analyzer
    sid = SentimentIntensityAnalyzer()
    
    #Ensure Text is in string format
    text = df_clean['text_cleaned']
    text = str(text).encode('utf-8')
    
    #Apply Sentiment Analyzer to text data, parse out dictionary value to columns
    df_clean['scores']=df_clean['text_cleaned'].apply(lambda text:sid.polarity_scores(str(text)))
    df_clean['comment_neg']=df_clean['scores'].apply(lambda score_dict: score_dict['neg'])
    df_clean['comment_neu']=df_clean['scores'].apply(lambda score_dict: score_dict['neu'])
    df_clean['comment_pos']=df_clean['scores'].apply(lambda score_dict: score_dict['pos'])
    df_clean['comment_compound']=df_clean['scores'].apply(lambda score_dict: score_dict['compound'])
  
    #Ensure values are in numeric format select necessary columns for analysis 
    df_clean["votes"] = pd.to_numeric(df_clean["votes"], errors='coerce')
    df_comm=df_clean[['video_id','votes','comment_neg','comment_neu','comment_pos','comment_compound']]
  
    #Group dataframe by video ID taking the mean of the comment values
    df_comments_all=df_comm.groupby(['video_id']).mean().reset_index()
  
    return df_comments_all

def ohe_ld_score(score):
    """
    Converts decimal ld_score into categorical -1,0,1
    """
    if score <= 0.5:
        return -1
    elif score < 0.75:
        return 0
    else:
        return 1

def conv_category(cat_name):
    """
    Converts category string to number based on our mapping dict from the youtube api.
    """
    try:
        cat_code = inv_cat_code_dict[cat_name]
    except:
        cat_code = 0
    return cat_code

def smooth_if_0(row):
    """
    Creates a smoothed view_like ratio feature to avoid division by zero for a more accurate reflection of the ratio.
    """
    if row["like_count"] == 0:
        vl_ratio = (row["view_count"]+1) / (row["like_count"]+1)
    else:
        vl_ratio = row["view_count"] / row["like_count"]
    return round(vl_ratio,2)

def prepare_data_for_model(df,only_eng=True):
    """
    Takes in a dataframe and performs processing on it to prepare for model training.
    """
    
    # Select columns we are interested in and replace NaN with 0
    df=df[['id','fetch_date','uploader','upload_date','title','desc_text','category',
        'duration','age_limit', 'view_count', 'like_count','dislike_count', 
        'average_rating', 'allow_embed', 'is_crawlable','allow_sub_contrib', 
        'is_live_content', 'is_ads_enabled','is_comments_enabled',
        'view_like_ratio', 'view_dislike_ratio','like_dislike_ratio',"dislike_like_ratio"]].replace(np.nan, 0)

    # Convert t,f to 0,1 booleans.
    df.allow_embed=df.allow_embed.map(dict(t=1, f=0))
    df.is_crawlable=df.is_crawlable.map(dict(t=1, f=0))
    df.allow_sub_contrib=df.allow_sub_contrib.map(dict(t=1, f=0))
    df.is_live_content=df.is_live_content.map(dict(t=1, f=0))
    df.is_ads_enabled=df.is_ads_enabled.map(dict(t=1, f=0))
    df.is_comments_enabled=df.is_comments_enabled.map(dict(t=1, f=0))
    df.replace([np.inf, -np.inf], np.nan,inplace=True)

    # Convert category column to pandas category type and then take the code to convert it to a numeric value
    df["category"] = df["category"].astype('category')
    df["cat_codes"] = df["category"].apply(conv_category)

    # Smooth view_like_ratio which helps avoid division by zero.
    df["view_like_ratio_smoothed"] = df.apply(lambda row: smooth_if_0(row),axis=1)

    # Create like_dislike_score
    df["ld_score"]=(df.like_count/(df.like_count + df.dislike_count))

    # Convert like_dislike_score into -1,0,1 categories for negative, neutral, and positive
    # These will be our y values for the models
    df["ld_score_ohe"] = df["ld_score"].apply(ohe_ld_score)
    
    # Adds sentiment and filters for english
    df = find_english(df,only_eng=only_eng)

    # Replace NaN with 0s
    df=df.replace(np.nan, 0)
    
    # TODO: Might need to normalize values
    
    # Print out the value counts
    print("ld_score_ohe value counts:")
    print(df["ld_score_ohe"].value_counts())
    print("Dataframe processed")
    
    return df

def create_final_dataframe(comment_df,archive_df,only_eng=True):
    """
    Processes comment df and archive df into one merged dataframe.
    
    Returns final merged dataframe
    """
    df_clean= clean_comments(comment_df)
    print("Comments cleaned.")
    df_comments_all= comment_sentiment(df_clean)
    print("Comments processed.")
    df_archive_all= prepare_data_for_model(archive_df,only_eng=only_eng)
    final_df=df_archive_all.merge(
        df_comments_all,
        how="left",
        left_on="id",
        right_on="video_id")
    final_df["NoComments"] = pd.isnull(final_df["comment_compound"])
    final_df["NoCommentsBinary"] = final_df["NoComments"].apply(lambda x: 1 if x==True else 0)
    final_df = final_df.replace(np.nan, 0)
    print("Comments and Archive data merged.")

    return final_df

def data_prep():
    """
    Runs data loading and processing pipeline.
    """

    # Get main dfs
    combined_df, randompctpoint2_df, comments_training_df, comments_testing_df = get_main_dfs()
    print("Retrieved initial dataframes.")

    # Process main dfs
    # Exports processed dataframes to processed folder as pickle files
    # We will export a training set focused on english videos and a testing set with all language videos.

    print("Processing training data...")
    training_df = create_final_dataframe(comments_training_df,combined_df)
    training_df.to_pickle(training_df_pickle_path)
    print(f"Training dataframe saved to {training_df_pickle_path}")

    print("Processing testing data...")
    testing_df = create_final_dataframe(comments_testing_df,randompctpoint2_df,only_eng=False)
    testing_df.to_pickle(testing_df_pickle_path)
    print(f"Testing dataframe saved to {testing_df_pickle_path}")


if __name__ == "__main__":
    data_prep()
    print("Dataframes ready for model training exported.")

