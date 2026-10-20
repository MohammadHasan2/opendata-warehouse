select
    snapshot_date,
    repository_id,
    full_name,
    language,
    stars,
    forks,
    watchers,
    open_issues,
    is_archived,
    is_fork
from {{ ref('stg_repository_snapshots') }}