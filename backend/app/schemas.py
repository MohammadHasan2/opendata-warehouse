
from typing import Any

from pydantic import BaseModel, ConfigDict


class OverviewResponse(BaseModel):
    repository_count: int
    total_stars: int
    total_forks: int
    total_open_issues: int


class LanguageSummaryResponse(BaseModel):
    language: str
    repository_count: int
    total_stars: int
    total_forks: int
    average_stars: float
    total_open_issues: int


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    repository_id: int
    full_name: str
    repository_name: str
    owner_login: str
    description: str | None = None
    language: str
    html_url: str
    is_archived: bool
    is_fork: bool
    stars: int
    forks: int
    watchers: int
    open_issues: int


class PaginationResponse(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class RepositoryFiltersResponse(BaseModel):
    language: str | None = None
    search: str | None = None


class RepositoryListResponse(BaseModel):
    data: list[RepositoryResponse]
    pagination: PaginationResponse
    filters: RepositoryFiltersResponse
