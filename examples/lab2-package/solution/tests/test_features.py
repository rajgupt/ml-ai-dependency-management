"""These tests import `churnkit` by name. No sys.path hacks anywhere in this repo."""

import pandas as pd

from churnkit import build_features, make_customers
from churnkit.features import TARGET


def test_target_is_never_a_feature():
    features = build_features(make_customers(200))
    assert TARGET not in features.columns


def test_derived_columns_exist():
    features = build_features(make_customers(200))
    assert {"spend_to_date", "calls_per_year"} <= set(features.columns)


def test_build_features_does_not_mutate_input():
    df = make_customers(200)
    before = df.copy()
    build_features(df)
    pd.testing.assert_frame_equal(df, before)
