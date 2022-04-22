import pandas as pd
import numpy as np
import joblib
from time import perf_counter

random_state = 42

# Vader for sentiment analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def smooth_if_0(row):
    """
    Creates a smoothed view_like ratio feature to avoid division by zero for a more accurate reflection of the ratio.
    """
    if row["like_count"] == 0:
        vl_ratio = (row["view_count"]+1) / (row["like_count"]+1)
    else:
        vl_ratio = row["view_count"] / row["like_count"]
    return round(vl_ratio,2)

def desc_sentiment(df):
    """
    Takes in a dataframe, performs vader sentiment analysis on it and outputs sentiment.
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

def prepare_data_for_pred(df):
    """
    Takes in a dataframe and performs processing on it to prepare for model training.
    """
    
    # Select columns we are interested in and replace NaN with 0
    df=df.replace(np.nan, 0)
    df.replace([np.inf, -np.inf], np.nan,inplace=True)

    # Smooth view_like_ratio which helps avoid division by zero.
    df["view_like_ratio_smoothed"] = df.apply(lambda row: smooth_if_0(row),axis=1)
    
    # Adds sentiment and filters for english
    df = desc_sentiment(df)

    # Replace NaN with 0s
    df=df.replace(np.nan, 0)
    
    # Print out the value counts
    print("Main Dataframe processed")
    
    return df

def create_final_dataframe(json_data, comment_df=None, archive_df=None):
    """
    Processes comment df and archive df into one merged dataframe.
    
    Returns final merged dataframe
    """

    X_cols = [
        "duration",
        "age_limit",
        "view_count",
        "like_count",
        "view_like_ratio_smoothed",
        "is_comments_enabled",
        "is_live_content",
        "cat_codes",
        "desc_neu",
        "desc_neg",
        "desc_pos",
        "desc_compound",
        "comment_neu",
        "comment_neg",
        "comment_pos",
        "comment_compound",
        "votes",
        "NoCommentsBinary"
    ]

    if comment_df is not None:
        df_clean= clean_comments(comment_df)
        print("Comments cleaned.")
        df_comments_all= comment_sentiment(df_clean)
        print("Comments processed.")
        df_archive_all= prepare_data_for_pred(archive_df)
        final_df=df_archive_all.merge(
            df_comments_all,
            how="left",
            left_on="id",
            right_on="video_id")
    else:
        print("No comments, skipping comment processing step.")
        final_df= prepare_data_for_pred(archive_df)
        final_df["votes"] = 0
        final_df["comment_neu"] = 0
        final_df["comment_neg"] = 0
        final_df["comment_pos"] = 0
        final_df["comment_compound"] = 0
        

    final_df = final_df.replace(np.nan, 0)

    # Make sure the columns are in the proper order and remove some unneeded columns.
    final_df = final_df[X_cols]
    print("Comments and Archive data merged.")
    
    json_data['view_like_ratio_smoothed'] = final_df.loc[0, 'view_like_ratio_smoothed']
    json_data['desc_neu'] = float(final_df.loc[0, 'desc_neu'])
    json_data['desc_neg'] = float(final_df.loc[0, 'desc_neg'])
    json_data['desc_pos'] = float(final_df.loc[0, 'desc_pos'])
    json_data['desc_compound'] = float(final_df.loc[0, 'desc_compound'])
    json_data['comment_neg'] = float(final_df.loc[0, 'comment_neg'])
    json_data['comment_neu'] = float(final_df.loc[0, 'comment_neu'])
    json_data['comment_pos'] = float(final_df.loc[0, 'comment_pos'])
    json_data['comment_compound'] = float(final_df.loc[0, 'comment_compound'])
    json_data['votes'] = int(final_df.loc[0, 'votes'])
    json_data['no_comment_binary'] = int(final_df.loc[0, 'NoCommentsBinary'])

    return final_df, json_data

def make_pred(pred_df,clf_path):
    start_load_time = perf_counter()
    rf_clf = joblib.load(clf_path)
    print(f"Time taken to load model: {(perf_counter() - start_load_time) }" )
    pred = rf_clf.predict(pred_df)
    
    return pred