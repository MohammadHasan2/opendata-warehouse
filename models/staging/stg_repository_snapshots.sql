select
    cast(snapshot_date as date) as snapshot_date,
    cast(repository_id as bigint) as repository_id,
    trim(full_name) as full_name,
    coalesce(nullif(trim(language), ''), 'Unknown') as language,
    cast(stars as bigint) as stars,
    cast(forks as bigint) as forks,
    cast(watchers as bigint) as watchers,
    cast(open_issues as bigint) as open_issues,
    cast(is_archived as boolean) as is_archived,
    cast(is_fork as boolean) as is_fork
from {{ source('github_data', 'repository_snapshots') }}
where snapshot_date is not null
  and repository_id is not null