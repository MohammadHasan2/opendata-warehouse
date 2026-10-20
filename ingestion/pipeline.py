"""Ingest GitHub repositories and maintain daily warehouse snapshots."""

import os
from pathlib import Path

import duckdb
import dlt
from dotenv import load_dotenv

from ingestion.github_source import github_repositories

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_daily_snapshot(database_path: Path) -> None:
    """Store the latest repository metrics, keeping one row per repo per day."""

    with duckdb.connect(str(database_path)) as connection:
        connection.execute("BEGIN TRANSACTION")

        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS github_data.repository_snapshots AS
                SELECT
                    CAST(NULL AS DATE) AS snapshot_date,
                    id AS repository_id,
                    full_name,
                    language,
                    stars,
                    forks,
                    watchers,
                    open_issues,
                    is_archived,
                    is_fork
                FROM github_data.repositories
                WHERE 1 = 0
            """)

            # Re-running today refreshes today's snapshot rather than duplicating it.
            connection.execute("""
                DELETE FROM github_data.repository_snapshots
                WHERE snapshot_date = CURRENT_DATE
            """)

            connection.execute("""
                INSERT INTO github_data.repository_snapshots
                SELECT
                    CURRENT_DATE AS snapshot_date,
                    id AS repository_id,
                    full_name,
                    language,
                    stars,
                    forks,
                    watchers,
                    open_issues,
                    is_archived,
                    is_fork
                FROM github_data.repositories
            """)

            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise

        count = connection.execute("""
            SELECT COUNT(*)
            FROM github_data.repository_snapshots
            WHERE snapshot_date = CURRENT_DATE
        """).fetchone()[0]

        print(f"Today's snapshot rows: {count}")


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    data_dir = Path(os.getenv("DUCKDB_DATA_DIR", str(PROJECT_ROOT / "data")))
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir

    data_dir.mkdir(parents=True, exist_ok=True)
    database_path = data_dir / "github_analytics.duckdb"

    query = os.getenv("GITHUB_QUERY", "stars:>1000")
    limit = int(os.getenv("GITHUB_REPO_LIMIT", "100"))
    per_page = int(os.getenv("GITHUB_PER_PAGE", "100"))

    if limit < 1:
        raise ValueError("GITHUB_REPO_LIMIT must be at least 1")
    if not 1 <= per_page <= 100:
        raise ValueError("GITHUB_PER_PAGE must be between 1 and 100")

    pipeline = dlt.pipeline(
        pipeline_name="github_analytics",
        destination=dlt.destinations.duckdb(str(database_path)),
        dataset_name="github_data",
    )

    print(f"Database: {database_path}")
    print(f"Search query: {query}")
    print(f"Repository limit: {limit}")

    load_info = pipeline.run(
        github_repositories(
            query=query,
            limit=limit,
            per_page=per_page,
        )
    )

    print("\nIngestion completed.")
    print(load_info)

    create_daily_snapshot(database_path)


if __name__ == "__main__":
    main()