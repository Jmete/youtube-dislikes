import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
import joblib

# For local testing
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

# Some paths for testing the function on local data.
ROOT_DIR = os.path.abspath(os.curdir)

# Path to save the model
model_pickle_path = os.path.join(ROOT_DIR,"models/rfclf.joblib.pkl")

# Test pred df
testing_df_pickle_path = os.path.join(ROOT_DIR,"data/processed/testing_df.pkl")
test_pred_df = pd.read_pickle(testing_df_pickle_path).iloc[0].to_frame().T
test_pred_row = test_pred_df[X_cols]
test_pred_actual = test_pred_df["ld_score_ohe"].values

def make_pred(pred_df,clf_path):
    print("Input data is:")
    print(pred_df)
    print("Loading model...")
    rf_clf = joblib.load(clf_path)
    print("Making Prediction...")
    pred = rf_clf.predict(pred_df)
    print(f"Prediction is: {pred}")
    return pred

if __name__ == "__main__":
    print("Testing predict model")
    make_pred(test_pred_row,model_pickle_path)
    print(f"Actual label was {test_pred_actual}")