
export interface Overview {
  repository_count: number
  total_stars: number
  total_forks: number
  total_open_issues: number
}

export interface LanguageSummary {
  language: string
  repository_count: number
  total_stars: number
  total_forks: number
  average_stars: number
  total_open_issues: number
}

export interface Repository {
  repository_id: number
  full_name: string
  repository_name: string
  owner_login: string
  description: string | null
  language: string
  html_url: string
  is_archived: boolean
  is_fork: boolean
  stars: number
  forks: number
  watchers: number
  open_issues: number
}

export interface RepositoryList {
  data: Repository[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
  filters: {
    language: string | null
    search: string | null
  }
}
