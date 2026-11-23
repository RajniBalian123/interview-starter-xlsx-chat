# Interview Starter — Spreadsheet Chat

A take-home / live-pairing interview exercise, rebuilt from scratch with
synthetic data. It ships with the boring parts already wired up — chat,
file upload, a queryable store — and one intentionally incomplete function
the candidate fills in: inferring real column types from sampled rows.

This is a personal demo project. It captures the pattern — a working
starter plus a focused candidate task plus a grading rubric — without any
client code, client data, or proprietary material.

## The idea

A good interview exercise is not a puzzle. It is a small piece of real
work, with the scaffolding done and exactly one interesting decision left
open. The candidate reads a real codebase, makes a real design choice, and
shows how they handle edge cases. The interviewer watches how they think,
not whether they memorise a trick.

## What's working out of the box

- **Upload** — load a `.csv` spreadsheet; rows are parsed and stored in
  SQLite (stdlib `sqlite3`).
- **Chat** — ask questions in plain words; the chat layer calls tools:
  - `list_data_sources` — what files were uploaded? Column metadata and
    row counts.
  - `query_data` — pull rows from a file with optional column projection
    and filters. Returns up to 200 rows.
- **Persistence** — chats and data sources survive a restart (SQLite file).

## What's intentionally missing

- Authentication, sessions, organizations, multi-tenancy.
- Embeddings / vector search.
- Background jobs, queues.
- Object storage — the original file bytes are not retained after parsing.

## The candidate task

The function lives in `src/parse_spreadsheet.py`, in `discover_column_schema`.
Today it just normalises headers to `snake_case` and marks every column as
`"unknown"`. The candidate's job:

1. Infer real column types from the sampled rows (`string` / `integer` /
   `float` / `boolean` / `date` / `datetime` / `currency`).
2. (Stretch) Generate a short, human-readable description per column.
3. (Stretch) Coerce values during parsing so `query_data` returns real
   numbers/booleans/dates instead of strings.
4. (Stretch) Surface the inferred type through `query_data` so the model
   knows which columns are numeric.

The reference implementation in this repo does (1) and (3); (2) and (4) are
left as the exercise, with tests showing what "done" looks like.

## Run it

```bash
python -m src.run_demo
```

Pure standard library, no dependencies. It loads the synthetic employee
spreadsheet, infers the column schema, and answers a few questions.

Run the checks:

```bash
python -m unittest discover -s tests -v
```

## Grading rubric

See `docs/design.md`. In short: type-inference quality, test coverage, how
cleanly they extend `query_data`, edge-case handling (empty cells, mixed
types, locale-formatted numbers), and whether they choose a deterministic
heuristic or an LLM call — and can defend the choice.

## Layout

- `src/parse_spreadsheet.py` — CSV parsing + `discover_column_schema`
  (the candidate task, reference implementation included).
- `src/store.py` — SQLite store: data sources and rows.
- `src/chat.py` — the deterministic chat layer over the two tools.
- `src/run_demo.py` — the demo runner.
- `data/sample_employees.csv` — synthetic employee data with edge cases.
- `docs/design.md` — the interview design and grading rubric.
- `tests/` — checks for type inference, coercion, and the chat tools.
