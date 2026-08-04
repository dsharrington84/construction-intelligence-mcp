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
            raise FileNotFoundError(f"DuckDB database not found: {self.database}")

    @contextmanager
    def connect(self) -> Iterator[duckdb.DuckDBPyConnection]:
        connection = duckdb.connect(str(self.database), read_only=True)
        try:
            yield connection
        finally:
            connection.close()

    def table_exists(self, table_name: str) -> bool:
        with self.connect() as connection:
            value = connection.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = ?
                """,
                [table_name],
            ).fetchone()
        return bool(value and value[0])

    def columns(self, table_name: str) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(f'DESCRIBE "{table_name}"').fetchall()
        return [str(row[0]) for row in rows]

    def fetch_all(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.connect() as connection:
            cursor = connection.execute(sql, list(parameters or []))
            names = [str(column[0]) for column in cursor.description]
            return [
                dict(zip(names, row, strict=True))
                for row in cursor.fetchall()
            ]

    def fetch_one(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> dict[str, Any] | None:
        rows = self.fetch_all(sql, parameters)
        return rows[0] if rows else None
