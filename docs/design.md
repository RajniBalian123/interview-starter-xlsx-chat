# Design: an interview exercise that shows how someone thinks

Status: demo of the exercise pattern, with synthetic data. The reference
implementation covers type inference and coercion; the description
generation and type-aware query stretch goals are left open.

## 1. Why a starter, not a blank page

A blank page tests whether someone can set up a project. A starter tests
whether they can read one, find the one place that matters, and change it
well. The starter ships with the boring parts wired up — chat, upload,
storage, tools — so the candidate's time goes to the interesting decision:
how do you infer a column's type from messy real rows?

## 2. The candidate task

`discover_column_schema` receives sampled rows and returns, per column, a
type and (stretch) a description. The reference implementation infers:

- `integer` — all non-empty values match `^[+-]?\d+$`
- `float` — all non-empty values parse as numbers with a decimal point or
  exponent, including locale-formatted `1,250.00`
- `boolean` — all non-empty values are in {true, false, yes, no}
- `date` / `datetime` — all non-empty values parse under a known format
- `currency` — values carry a currency symbol ($, €, £) with a numeric body
- `string` — anything else, including mixed types. Mixed is not an error;
  a column with numbers and text is a string column with messy data.

Edge cases that separate good answers from great ones:

- **Empty cells** are skipped, never typed. A column that is all empty is
  `string` with a note, not `unknown`.
- **Mixed types** fall back to `string`. Guessing the majority type hides
  data.
- **Locale numbers** (`1,250.00`, `1.250,00`) must be handled, not rejected.
- **1/0 is an integer, not a boolean**, unless the column also contains
  true/false/yes/no.
- **A date in two formats** (`2024-01-05` and `05/01/2024`) is ambiguous
  and must not be typed as a date on a guess.

## 3. Deterministic heuristic vs LLM call

The candidate must choose, and defend, one of two approaches:

- **Deterministic heuristic** (what the reference does): fast, free,
  testable, and wrong in exactly the ways you can enumerate. Best when the
  data is tabular and the types are a closed set.
- **LLM call** (the stretch): better at descriptions and ambiguous
  columns, but costs a call per column, is non-deterministic, and needs a
  fallback when the model is wrong. Best for the human-readable description,
  not for the type itself.

A strong answer uses the heuristic for types and the model for
descriptions — and says why.

## 4. Grading rubric

| Area | What good looks like |
|---|---|
| Type-inference quality | Correct types on the sample data; sensible fallback on mixed/empty |
| Test coverage | Tests for each type plus the edge cases above |
| `query_data` extension | Coerced values flow through; numeric columns are marked numeric |
| Edge cases | Empty cells, mixed types, locale numbers handled deliberately |
| Design judgement | Heuristic vs LLM choice defended; failure modes named |

## 5. Running it

- **Take-home:** hand over the repo, give 2–3 hours, ask for the
  implementation plus tests and a short note on the heuristic-vs-LLM choice.
- **Live pairing:** share the screen, ask them to implement one type
  (e.g. currency) and one edge case, then discuss the rest. 45 minutes.
- **Review:** run their tests, read the note, and ask one follow-up:
  "What would break your inference on a real customer's spreadsheet?"
