"""Demo runner: load the sample spreadsheet, infer its schema, ask questions."""

from pathlib import Path

from src.chat import answer
from src.parse_spreadsheet import (coerced_rows, discover_column_schema,
                                   parse_spreadsheet)
from src.store import Store

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = ROOT / "data" / "sample_employees.csv"
    headers, rows = parse_spreadsheet(path)
    schema = discover_column_schema(headers, rows)
    print(f"Loaded {path.name}: {len(rows)} rows")
    print("\nInferred column schema:")
    for h, info in schema.items():
        print(f"  {h:<14} {info['type']:<9} e.g. {info['sample']!r}")

    store = Store()
    store.add_source(path.name, headers, coerced_rows(headers, rows, schema))
    print()
    for question in (
        "what files do I have?",
        "show me 3 rows from sample_employees.csv",
        "average of salary in sample_employees.csv",
        "how many rows in sample_employees.csv",
    ):
        print(f"> {question}")
        print(answer(store, question))
        print()


if __name__ == "__main__":
    main()
