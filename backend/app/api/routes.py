from fastapi import APIRouter, HTTPException, Query

from app.database import check_database
from app.services.analytics import (
    get_overview,
    get_language_summary,
    get_repositories,
)
from app.schemas import (
    OverviewResponse,
    LanguageSummaryResponse,
    RepositoryListResponse,
)

router = APIRouter()


@router.get("/health")
def health_check():
    try:
        if check_database():
            return {"status": "healthy", "database": "connected"}
    except Exception:
        pass

    raise HTTPException(
        status_code=503,
        detail="Warehouse database is unavailable",
    )


@router.get("/api/overview",response_model=OverviewResponse)
def overview():
    try:
        return get_overview()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve overview analytics",
        ) from exc


@router.get("/api/languages", response_model=list[LanguageSummaryResponse])
def languages():
    try:
        return get_language_summary()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve language analytics",
        ) from exc

@router.get("/api/repositories", response_model=RepositoryListResponse)
def repositories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    language: str | None = Query(default=None, max_length=100),
    search: str | None = Query(default=None, max_length=200),
):
    try:
        return get_repositories(
            page=page,
            page_size=page_size,
            language=language,
            search=search,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve repositories",
        ) from exc