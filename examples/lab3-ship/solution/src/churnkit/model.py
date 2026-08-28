"""Train and evaluate. Deliberately small -- the packaging is the lesson."""

from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from churnkit.features import TARGET, build_features

RANDOM_STATE = 0


@dataclass(frozen=True)
class Result:
    """What a training run produced, and enough context to compare two runs."""

    model: HistGradientBoostingClassifier
    test_auc: float
    n_train: int
    n_test: int


def train(df: pd.DataFrame, max_iter: int = 120) -> Result:
    """Fit the churn model and score it on a held-out split."""
    features = build_features(df)
    target = df[TARGET]

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.25, random_state=RANDOM_STATE, stratify=target
    )

    model = HistGradientBoostingClassifier(max_iter=max_iter, random_state=RANDOM_STATE)
    model.fit(x_train, y_train)

    return Result(
        model=model,
        test_auc=evaluate(model, x_test, y_test),
        n_train=len(x_train),
        n_test=len(x_test),
    )


def evaluate(
    model: HistGradientBoostingClassifier, features: pd.DataFrame, target: pd.Series
) -> float:
    """ROC AUC on already-built features."""
    return float(roc_auc_score(target, model.predict_proba(features)[:, 1]))
