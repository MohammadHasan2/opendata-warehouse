with snapshot_changes as (
    select
        snapshot_date,
        repository_id,
        full_name,
        language,
        stars,
        forks,
        open_issues,

        lag(stars) over (
            partition by repository_id
            order by snapshot_date
        ) as previous_stars,

        lag(forks) over (
            partition by repository_id
            order by snapshot_date
        ) as previous_forks

    from {{ ref('fct_repository_snapshots') }}
)

select
    snapshot_date,
    repository_id,
    full_name,
    language,
    stars,
    forks,
    open_issues,
    previous_stars,
    previous_forks,
    stars - previous_stars as stars_gained,
    forks - previous_forks as forks_gained
from snapshot_changes