import csv
import statistics
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "github_analytics.duckdb"
RESULTS = ROOT / "benchmarks" / "benchmark_results.csv"

RUNS = 20
WARMUPS = 3

ON_DEMAND_SQL = """
WITH latest_snapshot AS (
    SELECT MAX(snapshot_date) AS snapshot_date
    FROM main.fct_repository_snapshots
),
latest_repositories AS (
    SELECT f.*
    FROM main.fct_repository_snapshots AS f
    JOIN latest_snapshot AS l
      ON f.snapshot_date = l.snapshot_date
)
SELECT
    language,
    COUNT(*) AS repository_count,
    SUM(stars) AS total_stars,
    SUM(forks) AS total_forks,
    ROUND(AVG(stars), 2) AS average_stars,
    SUM(open_issues) AS total_open_issues
FROM latest_repositories
GROUP BY language
ORDER BY language
"""

PRECOMPUTED_SQL = """
SELECT
    language,
    repository_count,
    total_stars,
    total_forks,
    average_stars,
    total_open_issues
FROM main.mart_language_summary
ORDER BY language
"""


def normalize(rows):
    """Normalize numeric values so both result sets can be compared."""
    return [
        (
            row[0],
            int(row[1]),
            int(row[2]),
            int(row[3]),
            round(float(row[4]), 2),
            int(row[5]),
        )
        for row in rows
    ]


def benchmark(connection, sql, label):
    """Warm up the query and return individual execution times in ms."""
    for _ in range(WARMUPS):
        connection.execute(sql).fetchall()

    timings_ms = []

    for _ in range(RUNS):
        start = time.perf_counter()
        connection.execute(sql).fetchall()
        elapsed_ms = (time.perf_counter() - start) * 1000
        timings_ms.append(elapsed_ms)

    return {
        "query": label,
        "runs": RUNS,
        "median_ms": round(statistics.median(timings_ms), 4),
        "min_ms": round(min(timings_ms), 4),
        "max_ms": round(max(timings_ms), 4),
    }


def main():
    if not DATABASE.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DATABASE}")

    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        # Check correctness before comparing performance.
        direct_rows = normalize(connection.execute(ON_DEMAND_SQL).fetchall())
        mart_rows = normalize(connection.execute(PRECOMPUTED_SQL).fetchall())

        if direct_rows != mart_rows:
            raise AssertionError(
                "The two queries returned different results. "
                "Fix correctness before benchmarking."
            )

        repository_count = connection.execute("""
            SELECT COUNT(*)
            FROM main.fct_repository_snapshots AS f
            WHERE f.snapshot_date = (
                SELECT MAX(snapshot_date)
                FROM main.fct_repository_snapshots
            )
        """).fetchone()[0]

        snapshot_count = connection.execute("""
            SELECT COUNT(*)
            FROM main.fct_repository_snapshots
        """).fetchone()[0]

        results = [
            benchmark(connection, ON_DEMAND_SQL, "on_demand_aggregation"),
            benchmark(connection, PRECOMPUTED_SQL, "precomputed_mart"),
        ]

    on_demand_ms = results[0]["median_ms"]
    mart_ms = results[1]["median_ms"]

    speedup = (
        round(on_demand_ms / mart_ms, 2)
        if mart_ms > 0
        else None
    )

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "query",
                "runs",
                "median_ms",
                "min_ms",
                "max_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print("Correctness check: PASSED")
    print(f"Repositories in latest snapshot: {repository_count}")
    print(f"Total snapshot rows: {snapshot_count}")
    print(f"Warm-up runs per query: {WARMUPS}")
    print(f"Measured runs per query: {RUNS}")
    print()

    for result in results:
        print(
            f"{result['query']}: "
            f"median={result['median_ms']} ms, "
            f"min={result['min_ms']} ms, "
            f"max={result['max_ms']} ms"
        )

    print(f"\nPrecomputed mart speedup: {speedup}x")
    print(f"Results saved to: {RESULTS}")


if __name__ == "__main__":
    main()