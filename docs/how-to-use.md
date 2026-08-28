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

No GPU is required. Lab 3 teaches GPU dependency *configuration*, which you can
write and validate on a laptop.

## Windows users

**The whole core path (M0–M8, Labs 1 and 2) runs on native Windows — no WSL
required.** `uv` is a first-class Windows tool and every `uv` command in this
book is identical on all three platforms.

The only things that differ are the handful of *shell* commands around the `uv`
calls — deleting a folder, writing a file, comparing two files. Command blocks
are written for `bash` (macOS/Linux). Where a block uses shell syntax that
PowerShell doesn't share, a **🪟 PowerShell** block follows it with the exact
equivalent. Two standing translations, so we don't repeat them everywhere:

| bash | PowerShell |
|---|---|
| `rm -rf .venv` | `Remove-Item -Recurse -Force .venv` |
| `cat file` | `Get-Content file` |
| `/tmp/x` | `$env:TEMP\x` |
| `./proof/bin/churn-train` | `.\proof\Scripts\churn-train.exe` |
| `cmd1 && cmd2` | `cmd1; if ($?) { cmd2 }` |

One more Windows-only detail, and it matters for [M6](06-gpu-and-system-deps.md):
Windows reports its CPU architecture as `AMD64`, not `x86_64`. When you write a
[PEP 508](https://peps.python.org/pep-0508/) marker to select a wheel, use
`platform_machine == 'AMD64'` for 64-bit Windows.

Use **PowerShell**, not the old `cmd.exe` — the here-strings and `Get-Content`
in the Windows blocks assume it. It ships with Windows 10 and 11.

## The labs

The three labs live in [`examples/`](../examples/lab1-bootstrap/starter/README.md).
Each has a `starter/` you work in and a `solution/` you compare against. They
build on each other, but each `starter/` is self-contained — you can start at
Lab 2 without doing Lab 1.
