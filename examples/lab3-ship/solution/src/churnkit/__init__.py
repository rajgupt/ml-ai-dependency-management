"""churnkit -- a small, boring, installable churn model.

The interesting thing about this package is not the model. It is that
`import churnkit` works from a notebook, from pytest, from a cron job and from
a container, without anyone touching `sys.path`.
"""

from churnkit.data import make_customers
from churnkit.features import build_features
from churnkit.model import evaluate, train

__all__ = ["build_features", "evaluate", "make_customers", "train"]
__version__ = "0.1.0"
