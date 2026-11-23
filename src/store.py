"""SQLite store: data sources and their rows (stdlib sqlite3)."""
from __future__ import annotations

import json
import sqlite3


class Store:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS data_source (
                id INTEGER PRIMARY KEY, name TEXT UNIQUE,
                columns_json TEXT, row_count INTEGER);
            CREATE TABLE IF NOT EXISTS data_source_row (
                id INTEGER PRIMARY KEY, source_id INTEGER,
                row_json TEXT,
                FOREIGN KEY (source_id) REFERENCES data_source(id));
        """)

    def add_source(self, name: str, columns: list[str],
                   rows: list[dict]) -> int:
        cur = self.conn.execute(
            "INSERT INTO data_source (name, columns_json, row_count) "
            "VALUES (?, ?, ?)", (name, json.dumps(columns), len(rows)))
        source_id = cur.lastrowid
        self.conn.executemany(
            "INSERT INTO data_source_row (source_id, row_json) VALUES (?, ?)",
            [(source_id, json.dumps(r, default=str)) for r in rows])
        self.conn.commit()
        return source_id

    def list_data_sources(self) -> list[dict]:
        cur = self.conn.execute(
            "SELECT name, columns_json, row_count FROM data_source")
        return [{"name": r["name"], "columns": json.loads(r["columns_json"]),
                 "row_count": r["row_count"]} for r in cur]

    def query_data(self, name: str, columns: list[str] | None = None,
                   filters: dict | None = None, limit: int = 200) -> list[dict]:
        cur = self.conn.execute(
            "SELECT row_json FROM data_source_row WHERE source_id = "
            "(SELECT id FROM data_source WHERE name = ?) LIMIT ?",
            (name, limit))
        rows = [json.loads(r["row_json"]) for r in cur]
        if filters:
            rows = [r for r in rows
                    if all(str(r.get(k, "")) == str(v)
                           for k, v in filters.items())]
        if columns:
            rows = [{c: r.get(c) for c in columns} for r in rows]
        return rows
