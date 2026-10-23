import { useEffect, useState } from 'react'
import { apiGet } from '../../shared/api'

const PAGE_SIZE = 12

function Cover({ book }) {
  const [failed, setFailed] = useState(false)

  if (!book.coverUrl || failed) {
    return (
      <div className="cover placeholder" aria-hidden="true">
        {book.title.charAt(0).toUpperCase()}
      </div>
    )
  }
  return (
    <img
      className="cover"
      src={book.coverUrl}
      alt=""
      loading="lazy"
      onError={() => setFailed(true)}
    />
  )
}

export function BookList({ onSelect }) {
  const [categories, setCategories] = useState([])
  const [draft, setDraft] = useState('')
  const [filters, setFilters] = useState({ q: '', category: '', page: 0 })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Danh sách thể loại cho ô lọc (tải một lần)
  useEffect(() => {
    apiGet('/books/categories')
      .then(setCategories)
      .catch(() => setCategories([]))
  }, [])

  // Tải danh sách mỗi khi bộ lọc hoặc trang đổi
  useEffect(() => {
    let active = true
    const params = new URLSearchParams({ page: filters.page, size: PAGE_SIZE })
    if (filters.q) params.set('q', filters.q)
    if (filters.category) params.set('category', filters.category)

    setLoading(true)
    setError('')
    apiGet(`/books?${params}`)
      .then((data) => { if (active) setResult(data) })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [filters])

  function handleSearch(event) {
    event.preventDefault()
    setFilters((prev) => ({ ...prev, q: draft.trim(), page: 0 }))
  }

  function handleCategory(event) {
    setFilters((prev) => ({ ...prev, category: event.target.value, page: 0 }))
  }

  function clearFilters() {
    setDraft('')
    setFilters({ q: '', category: '', page: 0 })
  }

  const books = result?.content ?? []
  const hasFilter = Boolean(filters.q || filters.category)

  return (
    <section className="panel">
      <h2>Kho sách</h2>

      <form className="toolbar" onSubmit={handleSearch}>
        <input
          type="search"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Tìm theo tên sách hoặc tác giả…"
          aria-label="Tìm kiếm sách"
        />
        <select value={filters.category} onChange={handleCategory} aria-label="Lọc theo thể loại">
          <option value="">Tất cả thể loại</option>
          {categories.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
        <button type="submit" className="btn primary">Tìm</button>
        {hasFilter && (
          <button type="button" className="btn" onClick={clearFilters}>Xóa lọc</button>
        )}
      </form>

      {error && <p className="error-text" role="alert">{error}</p>}
      {loading && !result && <p className="muted">Đang tải danh sách sách…</p>}

      {result && (
        <p className="muted result-count">
          {result.totalElements} sách
          {filters.q && <> khớp “{filters.q}”</>}
          {filters.category && <> trong thể loại “{filters.category}”</>}
        </p>
      )}

      {result && books.length === 0 && !loading && (
        <p className="muted">Không tìm thấy sách phù hợp.</p>
      )}

      <div className={`book-grid ${loading ? 'dimmed' : ''}`}>
        {books.map((book) => (
          <button
            key={book.id}
            type="button"
            className="book-card"
            onClick={() => onSelect(book.id)}
          >
            <Cover book={book} />
            <div className="book-card-body">
              <strong className="book-title">{book.title}</strong>
              <span className="book-author">{book.author}</span>
              <div className="chips">
                {book.categories.slice(0, 2).map((name) => (
                  <span key={name} className="chip">{name}</span>
                ))}
              </div>
              <span className="muted small">{book.chapterCount} chương</span>
            </div>
          </button>
        ))}
      </div>

      {result && result.totalPages > 1 && (
        <div className="pager">
          <button
            type="button"
            className="btn"
            disabled={filters.page === 0 || loading}
            onClick={() => setFilters((prev) => ({ ...prev, page: prev.page - 1 }))}
          >
            ← Trước
          </button>
          <span>Trang {result.page + 1} / {result.totalPages}</span>
          <button
            type="button"
            className="btn"
            disabled={filters.page + 1 >= result.totalPages || loading}
            onClick={() => setFilters((prev) => ({ ...prev, page: prev.page + 1 }))}
          >
            Sau →
          </button>
        </div>
      )}
    </section>
  )
}