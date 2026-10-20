from app.database import fetch_all


def get_overview() -> dict:
    """Return high-level repository analytics."""
    rows = fetch_all(
        """
        WITH latest_snapshot AS (
            SELECT MAX(snapshot_date) AS snapshot_date
            FROM main.fct_repository_snapshots
        )
        SELECT
            COUNT(*) AS repository_count,
            COALESCE(SUM(f.stars), 0) AS total_stars,
            COALESCE(SUM(f.forks), 0) AS total_forks,
            COALESCE(SUM(f.open_issues), 0) AS total_open_issues
        FROM main.fct_repository_snapshots AS f
        JOIN latest_snapshot AS latest
          ON f.snapshot_date = latest.snapshot_date
        """
    )

    return rows[0]


def get_language_summary() -> list[dict]:
    """Return precomputed language analytics from the dbt mart."""
    return fetch_all(
        """
        SELECT
            language,
            repository_count,
            total_stars,
            total_forks,
            average_stars,
            total_open_issues
        FROM main.mart_language_summary
        ORDER BY total_stars DESC
        """
    )

def get_repositories(
    page: int = 1,
    page_size: int = 20,
    language: str | None = None,
    search: str | None = None,
) -> dict:
    """Return paginated repositories with optional filters."""

    filters = []
    params = []

    if language and language.strip():
        filters.append("LOWER(language) = LOWER(?)")
        params.append(language.strip())

    if search and search.strip():
        filters.append("""
            (
                LOWER(full_name) LIKE LOWER(?)
                OR LOWER(repository_name) LIKE LOWER(?)
                OR LOWER(COALESCE(description, '')) LIKE LOWER(?)
            )
        """)
        pattern = f"%{search.strip()}%"
        params.extend([pattern, pattern, pattern])

    where_clause = (
        "WHERE " + " AND ".join(filters)
        if filters
        else ""
    )

    base_query = """
        WITH latest_snapshot AS (
            SELECT MAX(snapshot_date) AS snapshot_date
            FROM main.fct_repository_snapshots
        )
        SELECT
            d.repository_id,
            d.full_name,
            d.repository_name,
            d.owner_login,
            d.description,
            d.language,
            d.html_url,
            d.is_archived,
            d.is_fork,
            f.stars,
            f.forks,
            f.watchers,
            f.open_issues
        FROM main.dim_repositories AS d
        JOIN main.fct_repository_snapshots AS f
          ON d.repository_id = f.repository_id
        JOIN latest_snapshot AS latest
          ON f.snapshot_date = latest.snapshot_date
    """

    count_rows = fetch_all(
        f"""
        SELECT COUNT(*) AS total
        FROM ({base_query}) AS repositories
        {where_clause}
        """,
        params,
    )

    total = count_rows[0]["total"]

    rows = fetch_all(
        f"""
        SELECT *
        FROM ({base_query}) AS repositories
        {where_clause}
        ORDER BY stars DESC NULLS LAST, full_name
        LIMIT ? OFFSET ?
        """,
        params + [page_size, (page - 1) * page_size],
    )

    return {
        "data": rows,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
        "filters": {
            "language": language,
            "search": search,
        },
    }