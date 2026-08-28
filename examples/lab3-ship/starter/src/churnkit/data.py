"""Where rows come from.

In a real project this module talks to your warehouse. Here it generates
synthetic telco-style customers so the lab needs no credentials and no network.
"""

import numpy as np
import pandas as pd

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
