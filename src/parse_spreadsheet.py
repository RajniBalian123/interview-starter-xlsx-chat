"""Spreadsheet parsing + column-type inference.

The candidate task lives in discover_column_schema. The reference
implementation below infers real types from sampled rows; it is the bar
the candidate's work is judged against, not a secret answer.
"""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

INT_RE = re.compile(r"^[+-]?\d+$")
FLOAT_RE = re.compile(r"^[+-]?(\d{1,3}(,\d{3})+|\d+)(\.\d+)?([eE][+-]?\d+)?$")
CURRENCY_RE = re.compile(r"^[$€£]\s?[\d,]+(\.\d{2})?$")
BOOL_WORDS = {"true", "false", "yes", "no"}
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d")
DATETIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M")


def normalise_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")


def parse_spreadsheet(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = [normalise_header(h) for h in reader.fieldnames or []]
        rows = []
        for raw in reader:
            rows.append({normalise_header(k): (v or "").strip()
                         for k, v in raw.items() if k is not None})
        return headers, rows


def _coerce_number(value: str) -> float | None:
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def _try_formats(value: str, formats: tuple[str, ...]) -> bool:
    for fmt in formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def infer_type(values: list[str]) -> str:
    """Infer one column's type from its non-empty values.

    Empty cells are skipped. Mixed types fall back to string — guessing the
    majority type hides data. 1/0 alone is an integer, not a boolean.
    """
    present = [v for v in values if v != ""]
    if not present:
        return "string"
    lowered = [v.lower() for v in present]
    if all(v in BOOL_WORDS for v in lowered):
        return "boolean"
    if all(INT_RE.match(v) for v in present):
        return "integer"
    if all(CURRENCY_RE.match(v) for v in present):
        return "currency"
    if all(_try_formats(v, DATETIME_FORMATS) for v in present):
        return "datetime"
    if all(_try_formats(v, DATE_FORMATS) for v in present):
        return "date"
    if all(_coerce_number(v) is not None and ("." in v or "e" in v.lower())
           for v in present):
        return "float"
    return "string"


def coerce_value(value: str, col_type: str):
    if value == "":
        return None
    if col_type == "integer":
        return int(value)
    if col_type == "float":
        return _coerce_number(value)
    if col_type == "boolean":
        return value.lower() in {"true", "yes"}
    if col_type == "currency":
        return _coerce_number(value.lstrip("$€£").strip())
    if col_type in {"date", "datetime"}:
        for fmt in DATETIME_FORMATS + DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return value


def discover_column_schema(headers: list[str],
                           rows: list[dict[str, str]],
                           sample_size: int = 50) -> dict[str, dict]:
    """Return {column: {type, sample, description}} for each header.

    Stretch goal (2) — a human-readable description per column — is left
    open for the candidate; the reference returns a template description.
    """
    schema = {}
    sample = rows[:sample_size]
    for header in headers:
        values = [r.get(header, "") for r in sample]
        col_type = infer_type(values)
        example = next((v for v in values if v != ""), "")
        schema[header] = {
            "type": col_type,
            "sample": example,
            "description": f"{header.replace('_', ' ')} ({col_type})",
        }
    return schema


def coerced_rows(headers: list[str], rows: list[dict[str, str]],
                 schema: dict[str, dict]) -> list[dict]:
    return [{h: coerce_value(r.get(h, ""), schema[h]["type"])
             for h in headers} for r in rows]
