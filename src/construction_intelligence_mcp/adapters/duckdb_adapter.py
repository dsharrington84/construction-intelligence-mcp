from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Sequence

import duckdb


class DuckDBAdapter:
    """Read-only DuckDB access owned by the service layer."""

    def __init__(self, database: str | Path) -> None:
        self.database = Path(database).expanduser()
        if not self.database.is_file():
            raise FileNotFoundError(
                f"DuckDB database not found at '{self.database}'. "
                "Set CI_DATABASE to the readable source DuckDB file."
            )

    @contextmanager
    def connect(self) -> Iterator[duckdb.DuckDBPyConnection]:
        connection = duckdb.connect(str(self.database), read_only=True)
        try:
            yield connection
        finally:
            connection.close()

    def resolve_table(self, table_name: str) -> str | None:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_name = ?
                ORDER BY CASE WHEN table_schema = 'main' THEN 0 ELSE 1 END, table_schema
                """,
                [table_name],
            ).fetchall()
        if not rows:
            return None
        schema, name = rows[0]
        return f"{self.quote_identifier(str(schema))}.{self.quote_identifier(str(name))}"

    def relations(self) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY table_schema, table_name
                """
            ).fetchall()
        return [
            f"{self.quote_identifier(str(schema))}.{self.quote_identifier(str(name))}"
            for schema, name in rows
        ]

    def columns(self, qualified_table: str) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(f"DESCRIBE {qualified_table}").fetchall()
        return [str(row[0]) for row in rows]

    @staticmethod
    def quote_identifier(identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'

    def fetch_all(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.connect() as connection:
            cursor = connection.execute(sql, list(parameters or []))
            names = [str(column[0]) for column in cursor.description]
            return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]

    def fetch_one(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> dict[str, Any] | None:
        rows = self.fetch_all(sql, parameters)
        return rows[0] if rows else None
