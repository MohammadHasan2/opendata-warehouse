
import { useCallback, useEffect, useState } from 'react'
import {
  Activity,
  AlertCircle,
  ArrowUpRight,
  Code2,
  GitFork,
  RefreshCw,
  Search,
  Star,
  CircleDot,
  ChevronLeft,
  ChevronRight,
  Database,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  fetchLanguages,
  fetchOverview,
  fetchRepositories,
} from './api'
import type { Overview, LanguageSummary, RepositoryList } from './types'
import './App.css'

const numberFormat = new Intl.NumberFormat('en-US')

function formatNumber(value: number) {
  return numberFormat.format(value)
}

function App() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [languages, setLanguages] = useState<LanguageSummary[]>([])
  const [repositories, setRepositories] = useState<RepositoryList | null>(null)

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [language, setLanguage] = useState('')
  const [page, setPage] = useState(1)

  const [loadingSummary, setLoadingSummary] = useState(true)
  const [loadingRepositories, setLoadingRepositories] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadSummary() {
      setLoadingSummary(true)
      try {
        const [overviewData, languageData] = await Promise.all([
          fetchOverview(),
          fetchLanguages(),
        ])

        if (active) {
          setOverview(overviewData)
          setLanguages(languageData)
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Failed to load analytics.')
        }
      } finally {
        if (active) setLoadingSummary(false)
      }
    }

    void loadSummary()

    return () => {
      active = false
    }
  }, [])

  const loadRepositories = useCallback(async () => {
    setLoadingRepositories(true)
    setError('')

    try {
      const result = await fetchRepositories({
        page,
        page_size: 10,
        language: language || undefined,
        search: search || undefined,
      })
      setRepositories(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load repositories.')
    } finally {
      setLoadingRepositories(false)
    }
  }, [page, language, search])

  useEffect(() => {
    void loadRepositories()
  }, [loadRepositories])

  function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPage(1)
    setSearch(searchInput.trim())
  }

  function handleLanguageChange(value: string) {
    setLanguage(value)
    setPage(1)
  }

  const metrics = [
    {
      label: 'Repositories tracked',
      value: overview ? formatNumber(overview.repository_count) : '—',
      detail: 'Repositories in the latest snapshot',
      icon: Database,
    },
    {
      label: 'Total stars',
      value: overview ? formatNumber(overview.total_stars) : '—',
      detail: 'Combined GitHub stars',
      icon: Star,
    },
    {
      label: 'Total forks',
      value: overview ? formatNumber(overview.total_forks) : '—',
      detail: 'Community repository forks',
      icon: GitFork,
    },
    {
      label: 'Open issues',
      value: overview ? formatNumber(overview.total_open_issues) : '—',
      detail: 'Across tracked repositories',
      icon: CircleDot,
    },
  ]

  const pageInfo = repositories?.pagination
  const chartData = languages.slice(0, 8).map((item) => ({
    language: item.language,
    stars: item.total_stars,
    repositories: item.repository_count,
  }))

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Activity size={22} /></div>
          <div>
            <strong>OpenData</strong>
            <span>WAREHOUSE</span>
          </div>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>
        <div className="sidebar-link active">
          <Activity size={18} />
          <span>Overview</span>
        </div>
        <div className="sidebar-link">
          <Database size={18} />
          <span>Repositories</span>
        </div>
        <div className="sidebar-link">
          <Code2 size={18} />
          <span>Languages</span>
        </div>

        <div className="sidebar-bottom">
          <div className="pipeline-status">
            <span className="status-dot" />
            <div>
              <strong>Warehouse connected</strong>
              <small>DuckDB · FastAPI</small>
            </div>
          </div>
          <span className="sidebar-version">OpenData Warehouse v1.0</span>
        </div>
      </aside>

      <section className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Analytics <span>/</span> Overview</div>
          <div className="topbar-right">
            <span className="live-indicator"><span className="status-dot" /> API connected</span>
            <div className="avatar">OD</div>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">GITHUB DATA INTELLIGENCE</div>
              <h1>Warehouse overview</h1>
              <p>Explore repository activity, language trends, and community engagement.</p>
            </div>
            <button className="refresh-button" onClick={() => window.location.reload()}>
              <RefreshCw size={16} />
              Refresh data
            </button>
          </section>

          {error && (
            <div className="error-banner">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <section className="metric-grid">
            {metrics.map((metric) => {
              const Icon = metric.icon
              return (
                <article className="metric-card" key={metric.label}>
                  <div className="metric-top">
                    <span>{metric.label}</span>
                    <div className="metric-icon"><Icon size={18} /></div>
                  </div>
                  <div className="metric-value">
                    {loadingSummary ? <span className="skeleton-value" /> : metric.value}
                  </div>
                  <div className="metric-detail">{metric.detail}</div>
                </article>
              )
            })}
          </section>

          <section className="content-grid">
            <article className="panel chart-panel">
              <div className="panel-heading">
                <div>
                  <h2>Stars by language</h2>
                  <p>Top 8 languages by combined stars</p>
                </div>
                <span className="panel-tag">TOP LANGUAGES</span>
              </div>

              {loadingSummary ? (
                <div className="chart-placeholder">Loading language analytics…</div>
              ) : chartData.length === 0 ? (
                <div className="chart-placeholder">No language data available.</div>
              ) : (
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      layout="vertical"
                      margin={{ top: 4, right: 24, left: 12, bottom: 4 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e9edf4" />
                      <XAxis
                        type="number"
                        tickFormatter={(value: number) => numberFormat.format(value)}
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#7d8798', fontSize: 11 }}
                      />
                      <YAxis
                        type="category"
                        dataKey="language"
                        width={90}
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#505b6d', fontSize: 12 }}
                      />
                      <Tooltip
                        formatter={(value) => [formatNumber(Number(value)), 'Stars']}
                        contentStyle={{
                          borderRadius: 10,
                          border: '1px solid #e5eaf1',
                          boxShadow: '0 8px 24px rgba(25, 40, 70, 0.08)',
                        }}
                      />
                      <Bar dataKey="stars" fill="#5369e8" radius={[0, 5, 5, 0]} barSize={20} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="chart-footer">
                <span><span className="legend-dot" /> Total stars</span>
                <span>Source: dbt language mart</span>
              </div>
            </article>

            <article className="panel insight-panel">
              <div className="panel-heading">
                <div>
                  <h2>Language breakdown</h2>
                  <p>Repository distribution</p>
                </div>
                <Code2 size={19} className="muted-icon" />
              </div>

              <div className="language-list">
                {languages.slice(0, 5).map((item, index) => {
                  const total = languages.reduce((sum, row) => sum + row.repository_count, 0)
                  const percentage = total > 0 ? (item.repository_count / total) * 100 : 0

                  return (
                    <div className="language-row" key={item.language}>
                      <div className="language-row-top">
                        <div className="language-name">
                          <span className={`language-dot language-dot-${index}`} />
                          <span>{item.language}</span>
                        </div>
                        <strong>{formatNumber(item.repository_count)}</strong>
                      </div>
                      <div className="progress-track">
                        <div className={`progress-fill progress-fill-${index}`} style={{ width: `${percentage}%` }} />
                      </div>
                    </div>
                  )
                })}
                {!loadingSummary && languages.length === 0 && (
                  <div className="empty-state">No language breakdown available.</div>
                )}
              </div>

              <div className="insight-footer">
                <span>Showing top 5 languages</span>
                <span className="footer-icon"><ArrowUpRight size={15} /></span>
              </div>
            </article>
          </section>

          <section className="panel repository-panel">
            <div className="repository-heading">
              <div>
                <h2>Repository explorer</h2>
                <p>Search, filter, and inspect tracked GitHub repositories.</p>
              </div>
              <span className="result-count">
                {pageInfo ? `${formatNumber(pageInfo.total)} repositories` : 'Loading results…'}
              </span>
            </div>

            <form className="filter-bar" onSubmit={handleSearch}>
              <label className="search-field">
                <Search size={17} />
                <input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="Search repositories, owners, descriptions…"
                  aria-label="Search repositories"
                />
              </label>

              <select
                value={language}
                onChange={(event) => handleLanguageChange(event.target.value)}
                aria-label="Filter by programming language"
              >
                <option value="">All languages</option>
                {languages.map((item) => (
                  <option value={item.language} key={item.language}>{item.language}</option>
                ))}
              </select>

              <button type="submit" className="search-button">
                <Search size={16} />
                Search
              </button>
            </form>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>REPOSITORY</th>
                    <th>LANGUAGE</th>
                    <th><Star size={13} /> STARS</th>
                    <th><GitFork size={13} /> FORKS</th>
                    <th>OPEN ISSUES</th>
                    <th>STATUS</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {loadingRepositories ? (
                    <tr><td colSpan={7} className="table-message">Loading repositories…</td></tr>
                  ) : repositories?.data.length ? (
                    repositories.data.map((repo) => (
                      <tr key={repo.repository_id}>
                        <td>
                          <div className="repo-name">{repo.full_name}</div>
                          <div className="repo-description">{repo.description || 'No description provided'}</div>
                        </td>
                        <td><span className="language-badge">{repo.language}</span></td>
                        <td className="numeric-cell">{formatNumber(repo.stars)}</td>
                        <td className="numeric-cell">{formatNumber(repo.forks)}</td>
                        <td className="numeric-cell">{formatNumber(repo.open_issues)}</td>
                        <td>
                          <span className={`status-badge ${repo.is_archived ? 'archived' : 'active-status'}`}>
                            <span className="status-dot" />
                            {repo.is_archived ? 'Archived' : 'Active'}
                          </span>
                        </td>
                        <td>
                          <a
                            className="repo-link"
                            href={repo.html_url}
                            target="_blank"
                            rel="noreferrer"
                            aria-label={`Open ${repo.full_name} on GitHub`}
                          >
                            <ArrowUpRight size={17} />
                          </a>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan={7} className="table-message">No repositories match your filters.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="pagination-bar">
              <span>
                {pageInfo && pageInfo.total > 0
                  ? `Page ${pageInfo.page} of ${pageInfo.total_pages} · ${formatNumber(pageInfo.total)} results`
                  : 'No results'}
              </span>
              <div className="pagination-actions">
                <button
                  disabled={!pageInfo || pageInfo.page <= 1 || loadingRepositories}
                  onClick={() => setPage((current) => current - 1)}
                  aria-label="Previous page"
                >
                  <ChevronLeft size={17} />
                  Previous
                </button>
                <button
                  disabled={!pageInfo || pageInfo.page >= pageInfo.total_pages || loadingRepositories}
                  onClick={() => setPage((current) => current + 1)}
                  aria-label="Next page"
                >
                  Next
                  <ChevronRight size={17} />
                </button>
              </div>
            </div>
          </section>

          <footer className="page-footer">
            <span><Database size={14} /> Powered by Python, dlt, dbt Core, DuckDB & FastAPI</span>
            <span>Analytics from your latest warehouse snapshot</span>
          </footer>
        </div>
      </section>
    </main>
  )
}

export default App
