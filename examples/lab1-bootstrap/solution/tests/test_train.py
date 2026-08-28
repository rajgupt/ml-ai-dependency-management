"""These tests do NOT pass yet. That is deliberate -- see step 8 of Lab 1.

`from train import make_customers` fails with `ModuleNotFoundError: No module
named 'train'`, because this project is not installable: pytest has no reason
to put the project root on `sys.path`. The fix is not a `sys.path.append`, it
is packaging. That is Lab 2.
"""

from train import make_customers


def test_customers_are_deterministic():
    assert make_customers(200).equals(make_customers(200))


def test_churn_is_labelled_zero_or_one():
    assert set(make_customers(200)["churned"].unique()) <= {0, 1}
