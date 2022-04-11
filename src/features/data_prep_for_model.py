# This script takes in our csv files that were exported as a training and test set from our main dataset from our database.
# It processes the data and prepares it for model training including type casting, handling NaN or null values, and sentiment analysis features.
# It will also process comment data that was scraped, perform sentiment analysis on them, and join them with the main dataset as extra features.

import pandas as pd
import numpy as np
import pickle
import os

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
# TODO: ADD COMMENT CSV FILES AFTER EXPORT

# Pickle save paths
training_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/training_df.pkl")
testing_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/testing_df.pkl")

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

    return combined_df, randompctpoint2_df

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

    data['neu']=data['scores'].apply(lambda score_dict: score_dict['neu'])                        #Extract Neutral Values from dictionary
    data['neg']=data['scores'].apply(lambda score_dict: score_dict['neg'])                        #Extract Negative Values from dictionary
    data['pos']=data['scores'].apply(lambda score_dict: score_dict['pos'])                        #Extract Positive Values from dictionary
    data['compound']=data['scores'].apply(lambda score_dict: score_dict['compound'])              #Extract Compound Values from dictionary

    combined_data=pd.concat([df,data], axis=1).reindex(df.index)                    #Add values back to original dataframe

    # If only eng is true, filter for only english, else return all the data
    if only_eng:
        eng_data= combined_data[combined_data['neu'] != 1]                              #Filter out df values with a neu score of 1 (indicate foreign desc)
        return eng_data
    else:
        return combined_data


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
    df["cat_codes"] = df["category"].cat.codes

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

def data_prep():
    """
    Runs data loading and processing pipeline.
    """

    # Get main dfs
    combined_df, randompctpoint2_df = get_main_dfs()
    print("Retrieved initial dataframes.")

    # Process main dfs
    # Exports processed dataframes to processed folder as pickle files
    # We will export a training set focused on english videos and a testing set with all language videos.

    print("Processing training data...")
    training_df = prepare_data_for_model(combined_df)
    training_df.to_pickle(training_df_pickle_path)
    print(f"Training dataframe saved to {training_df_pickle_path}")

    print("Processing testing data...")
    testing_df = prepare_data_for_model(randompctpoint2_df,only_eng=False)
    testing_df.to_pickle(testing_df_pickle_path)
    print(f"Testing dataframe saved to {testing_df_pickle_path}")


if __name__ == "__main__":
    data_prep()
    print("Dataframes ready for model training exported.")

