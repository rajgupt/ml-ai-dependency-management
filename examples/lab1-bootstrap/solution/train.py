"""Train a churn classifier on synthetic telco-style data.

No downloads, no GPU, runs in a couple of seconds. The point of this script is
not the model -- it is that you can hand it to a colleague and they get the
same number you did.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

RANDOM_STATE = 0


def make_customers(n: int = 8_000, seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Synthetic customers whose churn depends on tenure, price and support calls."""
    rng = np.random.default_rng(seed)
    tenure_months = rng.integers(1, 72, size=n)
    monthly_charge = rng.normal(70, 25, size=n).clip(15, 160)
    support_calls = rng.poisson(1.2, size=n)
    is_month_to_month = rng.binomial(1, 0.55, size=n)

    logit = (
        -1.1
        - 0.045 * tenure_months
        + 0.021 * monthly_charge
        + 0.38 * support_calls
        + 1.05 * is_month_to_month
    )
    churned = rng.binomial(1, 1 / (1 + np.exp(-logit)))

    return pd.DataFrame(
        {
            "tenure_months": tenure_months,
            "monthly_charge": monthly_charge,
            "support_calls": support_calls,
            "is_month_to_month": is_month_to_month,
            "churned": churned,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the churn baseline.")
    parser.add_argument("--rows", type=int, default=8_000)
    parser.add_argument("--out", type=Path, default=Path("metrics.json"))
    args = parser.parse_args()

    df = make_customers(args.rows)
    features = df.drop(columns="churned")
    target = df["churned"]

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.25, random_state=RANDOM_STATE, stratify=target
    )

    model = HistGradientBoostingClassifier(max_iter=120, random_state=RANDOM_STATE)
    model.fit(x_train, y_train)
    auc = roc_auc_score(y_test, model.predict_proba(x_test)[:, 1])

    metrics = {"rows": int(args.rows), "test_auc": round(float(auc), 4)}
    args.out.write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"test AUC: {auc:.4f}  ->  {args.out}")


if __name__ == "__main__":
    main()
