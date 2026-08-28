# How to use this book

This is a cookbook. Read it next to a terminal, not on a train.

## Three routes

Pick one. Every page is badged so you can tell what applies to you.

| Badge | Means |
|---|---|
| 🟢 | Everyone — works on any project you touch |
| 🔵 | You own a repo — packaging, CI, lock policy |
| 🔴 | You own the platform — registries, base images, org-wide policy |

| Route | Who it's for | Time | Path |
|---|---|---|---|
| **Full** | New to Python packaging | ~3 h | M0 → M8, all three labs |
| **Fast** | Senior engineers who just want the recipes | ~75 min | M2, M4, M6, Lab 1, Checklist |
| **Notebook-first** | Analysts and researchers | ~90 min | M0, M1, M2, Lab 1, M7 |

## Page shape

Every module page has the same six sections, so you can skim to the part you need:

1. **3 a.m. story** — the symptom you'll recognise
2. **What's actually going on** — the minimum theory, never more
3. **🍳 Recipe** — copy-pasteable commands
4. **⚠️ Sharp edges** — the two or three ways this bites
5. **✅ Check yourself** — two questions
6. **📖 Go deeper** — at most three links

## What you need installed

- Python 3.11+ (the labs pin 3.12; `uv` will fetch it for you)
- `uv` — [installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
- Git
- Docker (Lab 3 only — skip it and you still get the configuration lesson)

No GPU is required. Lab 3 teaches GPU dependency *configuration*, which you can
write and validate on a laptop.

## The labs

The three labs live in [`examples/`](../examples/lab1-bootstrap/starter/README.md).
Each has a `starter/` you work in and a `solution/` you compare against. They
build on each other, but each `starter/` is self-contained — you can start at
Lab 2 without doing Lab 1.
