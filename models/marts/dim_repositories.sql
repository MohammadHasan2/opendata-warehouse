select
    repository_id,
    full_name,
    repository_name,
    owner_login,
    description,
    language,
    created_at,
    updated_at,
    is_archived,
    is_fork,
    html_url
from {{ ref('stg_repositories') }}