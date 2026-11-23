"""Deterministic chat layer over the two tools: list and query data sources."""
from __future__ import annotations

import re

from .store import Store


def list_data_sources(store: Store) -> str:
    sources = store.list_data_sources()
    if not sources:
        return "No files uploaded yet."
    lines = ["Files uploaded:"]
    for s in sources:
        lines.append(f"- {s['name']}: {s['row_count']} rows, "
                     f"columns {', '.join(s['columns'])}")
    return "\n".join(lines)


def query_data(store: Store, name: str, columns: list[str] | None = None,
               filters: dict | None = None, limit: int = 200) -> str:
    rows = store.query_data(name, columns, filters, limit)
    if not rows:
        return f"No rows found in {name}."
    lines = [f"{len(rows)} row(s) from {name}:"]
    for r in rows:
        lines.append("  " + ", ".join(f"{k}={v}" for k, v in r.items()))
    return "\n".join(lines)


def answer(store: Store, question: str) -> str:
    q = question.strip().lower()
    if "what files" in q or "list" in q and "file" in q:
        return list_data_sources(store)
    m = re.search(r"show me (\d+) rows? from (\S+)", q)
    if m:
        return query_data(store, m.group(2), limit=int(m.group(1)))
    m = re.search(r"average of (\S+) in (\S+)", q)
    if m:
        rows = store.query_data(m.group(2))
        values = [r[m.group(1)] for r in rows
                  if isinstance(r.get(m.group(1)), (int, float))]
        if not values:
            return f"No numeric values for {m.group(1)} in {m.group(2)}."
        return (f"Average {m.group(1)} in {m.group(2)}: "
                f"{sum(values) / len(values):,.2f} over {len(values)} rows.")
    m = re.search(r"how many rows (?:in|does) (\S+)", q)
    if m:
        rows = store.query_data(m.group(1))
        return f"{m.group(1)} has {len(rows)} row(s)."
    return ("I can list your files, show rows from a file, or average a "
            "numeric column. Try: 'what files do I have?' or "
            "'show me 5 rows from employees.csv'.")
