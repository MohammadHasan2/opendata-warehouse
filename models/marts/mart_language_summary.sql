with latest_snapshot as (
    select max(snapshot_date) as snapshot_date
    from {{ ref('fct_repository_snapshots') }}
),

latest_repositories as (
    select f.*
    from {{ ref('fct_repository_snapshots') }} as f
    inner join latest_snapshot as l
        on f.snapshot_date = l.snapshot_date
)

select
    language,
    count(*) as repository_count,
    sum(stars) as total_stars,
    sum(forks) as total_forks,
    round(avg(stars), 2) as average_stars,
    sum(open_issues) as total_open_issues
from latest_repositories
group by language