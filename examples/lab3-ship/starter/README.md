# Lab 3 · starter

This is the finished `churnkit` from [Lab 2](../../lab2-package/solution) —
installable, tested, no `sys.path` hacks. It runs on your laptop and nowhere
else: no GPU story, no container, no CI, and the lock is one dependency behind
on purpose.

Your job: make it run on a laptop *and* a GPU cluster from one lockfile, wrap
it in two containers, add CI that fails on a stale lock, and survive an
upgrade that quietly moves the model's AUC.

```bash
uv sync
uv run churn-train --rows 8000     # test AUC: 0.7473 (scikit-learn 1.3.2 -- see Step 4)
uv run pytest -q                   # passes
```

Full brief: [`docs/labs/lab-3.md`](../../../docs/labs/lab-3.md).
Compare against [`../solution`](../solution) when you're done — not before.
