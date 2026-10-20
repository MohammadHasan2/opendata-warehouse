
"""Extract public GitHub repository metadata."""

import time
from collections.abc import Iterator
from typing import Any

import dlt
import httpx

GITHUB_API = "https://api.github.com"


def get_json(
    client: httpx.Client,
    url: str,
    params: dict[str, Any],
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Request JSON with bounded retries for transient API failures."""

    for attempt in range(max_attempts):
        try:
            response = client.get(url, params=params)

            if response.status_code in (429, 500, 502, 503, 504):
                if attempt == max_attempts - 1:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")
                delay = min(float(retry_after), 10) if retry_after else 2**attempt
                time.sleep(delay)
                continue

            # GitHub can return 403 when a rate limit is exhausted.
            if response.status_code == 403:
                remaining = response.headers.get("X-RateLimit-Remaining")
                if remaining == "0":
                    reset_at = response.headers.get("X-RateLimit-Reset")
                    if reset_at and attempt < max_attempts - 1:
                        wait_seconds = max(int(reset_at) - int(time.time()), 1)
                        time.sleep(min(wait_seconds, 10))
                        continue

            response.raise_for_status()
            return response.json()

        except httpx.TransportError:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2**attempt)

    raise RuntimeError("GitHub API request failed after retries.")


@dlt.resource(
    name="repositories",
    write_disposition="merge",
    primary_key="id",
)
def github_repositories(
    query: str = "stars:>1000",
    limit: int = 100,
    per_page: int = 100,
) -> Iterator[dict[str, Any]]:
    """Yield a bounded number of repositories sorted by star count."""

    if limit < 1:
        raise ValueError("limit must be at least 1")

    if not 1 <= per_page <= 100:
        raise ValueError("per_page must be between 1 and 100")

    collected = 0
    page = 1

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "OpenData-Warehouse",
    }

    with httpx.Client(
        headers=headers,
        timeout=20.0,
        follow_redirects=True,
    ) as client:
        while collected < limit:
            current_page_size = min(per_page, limit - collected)

            payload = get_json(
                client,
                f"{GITHUB_API}/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": current_page_size,
                    "page": page,
                },
            )

            items = payload.get("items", [])
            if not items:
                break

            for repo in items:
                owner = repo.get("owner") or {}

                yield {
                    "id": repo["id"],
                    "full_name": repo["full_name"],
                    "name": repo["name"],
                    "owner_login": owner.get("login"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "watchers": repo.get("subscribers_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "is_archived": repo.get("archived", False),
                    "is_fork": repo.get("fork", False),
                    "html_url": repo.get("html_url"),
                }

                collected += 1
                if collected >= limit:
                    break

            if len(items) < current_page_size:
                break

            page += 1
