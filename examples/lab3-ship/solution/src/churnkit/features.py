"""Feature engineering, in one place, so the notebook and the training job agree.

This is the module that most often lives duplicated in three notebooks with
three slightly different definitions of `spend_per_month`. Don't do that.
"""

import pandas as pd

TARGET = "churned"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive model inputs from raw customer rows."""
    features = df.drop(columns=[TARGET], errors="ignore").copy()
    features["spend_to_date"] = features["monthly_charge"] * features["tenure_months"]
    features["calls_per_year"] = features["support_calls"] / (
        features["tenure_months"] / 12
    )
    return features
