"""The console script.

`[project.scripts]` in pyproject.toml points at `main` here, which is why you
can type `churn-train` instead of `python scripts/train_v3_final_FINAL.py` --
from any directory, in any container, at any version.
"""

import argparse
import json
from pathlib import Path

from churnkit.data import make_customers
from churnkit.model import train


def main() -> None:
    parser = argparse.ArgumentParser(prog="churn-train", description="Train the churn baseline.")
    parser.add_argument("--rows", type=int, default=8_000)
    parser.add_argument("--max-iter", type=int, default=120)
    parser.add_argument("--out", type=Path, default=Path("metrics.json"))
    args = parser.parse_args()

    result = train(make_customers(args.rows), max_iter=args.max_iter)

    metrics = {
        "rows": args.rows,
        "n_train": result.n_train,
        "n_test": result.n_test,
        "test_auc": round(result.test_auc, 4),
    }
    args.out.write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"test AUC: {result.test_auc:.4f}  ->  {args.out}")


if __name__ == "__main__":
    main()
