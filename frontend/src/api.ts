
import type {
  Overview,
  LanguageSummary,
  RepositoryList,
} from './types'

async function request<T>(path: string): Promise<T> {
  const response = await fetch(path)

  if (!response.ok) {
    const message = await response.text()
    throw new Error(
      `API request failed (${response.status}): ${message}`,
    )
  }

  return response.json() as Promise<T>
}

export function fetchOverview(): Promise<Overview> {
  return request<Overview>('/api/overview')
}

export function fetchLanguages(): Promise<LanguageSummary[]> {
  return request<LanguageSummary[]>('/api/languages')
}

export interface RepositoryQuery {
  page?: number
  page_size?: number
  language?: string
  search?: string
}

export function fetchRepositories(
  query: RepositoryQuery = {},
): Promise<RepositoryList> {
  const params = new URLSearchParams()

  params.set('page', String(query.page ?? 1))
  params.set('page_size', String(query.page_size ?? 20))

  if (query.language) {
    params.set('language', query.language)
  }

  if (query.search) {
    params.set('search', query.search)
  }

  return request<RepositoryList>(
    `/api/repositories?${params.toString()}`,
  )
}
