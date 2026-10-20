select
    cast(id as bigint) as repository_id,
    trim(full_name) as full_name,
    trim(name) as repository_name,
    owner_login,
    description,
    coalesce(nullif(trim(language), ''), 'Unknown') as language,
    cast(stars as bigint) as stars,
    cast(forks as bigint) as forks,
    cast(watchers as bigint) as watchers,
    cast(open_issues as bigint) as open_issues,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at,
    cast(is_archived as boolean) as is_archived,
    cast(is_fork as boolean) as is_fork,
    html_url
from {{ source('github_data', 'repositories') }}
where id is not null
  and full_name is not null