# This script loads our processed dataframes and uses them to train a Random Forest Classifier.
# We chose the RF since it seemed to have the best overall performance and efficiency while still being interpretable.

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
import joblib

from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef
from sklearn.ensemble import RandomForestClassifier

random_state = 42

ROOT_DIR = os.path.abspath(os.curdir)

# Pickle load paths for processed dataframes
training_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/training_df.pkl")
testing_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/testing_df.pkl")

# Path to save the model
model_pickle_path = os.path.join(ROOT_DIR,"models/rfclf.joblib.pkl")

# Columns of interest
# Based on what we can get at inference time from the Youtube API or scraping
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

y_col = "ld_score_ohe"

def test_model_metrics(clf, model_name,X_test,y_test):
    testpreds = clf.predict(X_test)
    acc = accuracy_score(y_test,testpreds)
    f1_scores_dict = {}
    if len(y_test.unique()) > 2:
        f1_scores_dict["f1_weighted"] = f1_score(y_test,testpreds,average="weighted")
    else:
        f1_scores_dict["f1_binary"] = f1_score(y_test,testpreds,average="binary")
        
    f1_scores_dict["f1_macro"] = f1_score(y_test,testpreds,average="macro")
    f1_scores_dict["f1_micro"] = f1_score(y_test,testpreds,average="micro")
    
    mcc = matthews_corrcoef(y_test,testpreds)

    print(f"{model_name} metrics:")
    print(f"Accuracy Score: {acc}")
    print(f"F1 scores: {f1_scores_dict}")
    print(f"MCC: {mcc}")
    return acc,f1_scores_dict,mcc

def train_model(training_df_pickle_path,testing_df_pickle_path,X_cols,y_col):
    """
    Trains a Random Forest Classifier on our training data. Prints out test metrics.

    Returns:
        RandomForestClassifier - Fit to training data
    """
    print("Loading training and testing dataframes...")
    training_df = pd.read_pickle(training_df_pickle_path)
    testing_df = pd.read_pickle(testing_df_pickle_path)

    # Helps tune the RF to be more accurate for negative videos since that is our main goal.
    class_weight_dict = {-1:0.1,0:1,1:2}

    print("Training model...")
    # Training model
    rf_clf = RandomForestClassifier(
        n_jobs=-1,
        random_state=random_state,
        class_weight = class_weight_dict,
        )
    rf_clf.fit(training_df[X_cols],training_df[y_col])

    print("Testing performance...")
    # Testing model
    test_model_metrics(rf_clf,"Random Forest",testing_df[X_cols],testing_df[y_col])

    return rf_clf

def save_model(clf,save_path):
    """
    Takes in a classifier object and saves it via joblib.pkl.
    This model can then be loaded to be used at inference time.
    """
    joblib.dump(clf, save_path, compress=3)


if __name__ == "__main__":
    rf_clf = train_model(training_df_pickle_path,testing_df_pickle_path,X_cols,y_col)
    print("Model finished trained.")
    print("Saving model...")
    save_model(rf_clf,model_pickle_path)
    print("Model saved.")