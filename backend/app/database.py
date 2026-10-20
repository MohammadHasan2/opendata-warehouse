from pathlib import Path

import duckdb


# Project root: D:\opendata-warehouse
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Existing warehouse created by dlt
DATABASE_PATH = PROJECT_ROOT / "data" / "github_analytics.duckdb"


def get_connection():
    """Open a read-only connection to the existing warehouse."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse database not found: {DATABASE_PATH}"
        )

    return duckdb.connect(str(DATABASE_PATH), read_only=True)


def fetch_all(sql: str, params: list | None = None) -> list[dict]:
    """Execute a read-only query and return rows as dictionaries."""
    connection = get_connection()

    try:
        result = connection.execute(sql, params or [])
        columns = [column[0] for column in result.description]
        rows = result.fetchall()

        return [
            dict(zip(columns, row))
            for row in rows
        ]
    finally:
        connection.close()


def check_database() -> bool:
    """Return True if the warehouse can be queried."""
    rows = fetch_all("SELECT 1 AS healthy")
    return rows[0]["healthy"] == 1