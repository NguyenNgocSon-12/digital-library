import { useEffect, useState } from 'react'
import { apiDelete, apiGet } from '../../shared/api'
import { useAuth } from '../../shared/auth-context'
import { BookForm } from './BookForm'
import { ChapterForm } from './ChapterForm'

const PAGE_SIZE = 10

function ChapterManager({ book, onBack, onChanged }) {
  const [adding, setAdding] = useState(false)
  const [error, setError] = useState('')

  async function handleDelete(chapter) {
    const ok = window.confirm(`Xóa chương ${chapter.chapterNo}: “${chapter.title}”?`)
    if (!ok) return
    setError('')
    try {
      await apiDelete(`/books/${book.id}/chapters/${chapter.chapterNo}`)
      onChanged('Đã xóa chương.')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <button type="button" className="btn" onClick={onBack}>← Về danh sách quản trị</button>
      <h3>Chương của “{book.title}”</h3>

      {error && <p className="error-text" role="alert">{error}</p>}

      {book.chapters.length === 0 && <p className="muted">Sách chưa có chương nào.</p>}
      <ol className="toc">
        {book.chapters.map((chapter) => (
          <li key={chapter.chapterNo} className="chapter-row">
            <span>
              Chương {chapter.chapterNo}: {chapter.title}
              {chapter.sectionHeadings.length > 0 && (
                <span className="muted small"> · {chapter.sectionHeadings.length} mục</span>
              )}
            </span>
            <button type="button" className="btn danger small-btn" onClick={() => handleDelete(chapter)}>
              Xóa
            </button>
          </li>
        ))}
      </ol>

      {adding ? (
        <ChapterForm
          book={book}
          onCancel={() => setAdding(false)}
          onSaved={() => {
            setAdding(false)
            onChanged('Đã thêm chương mới.')
          }}
        />
      ) : (
        <button type="button" className="btn primary" onClick={() => setAdding(true)}>
          + Thêm chương
        </button>
      )}
    </div>
  )
}

function AdminBooks() {
  const [view, setView] = useState('list') // list | create | edit | chapters
  const [selected, setSelected] = useState(null)
  const [page, setPage] = useState(0)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  // Tải bảng sách mỗi khi đổi trang hoặc có thay đổi dữ liệu
  useEffect(() => {
    let active = true
    setLoading(true)
    apiGet(`/books?page=${page}&size=${PAGE_SIZE}`)
      .then((data) => { if (active) { setResult(data); setError('') } })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [page, reloadKey])

  const reload = () => setReloadKey((key) => key + 1)

  function backToList(message = '') {
    setNotice(message)
    setView('list')
    setSelected(null)
    reload()
  }

  async function openBook(bookId, nextView) {
    setError('')
    setNotice('')
    try {
      const detail = await apiGet(`/books/${bookId}`)
      setSelected(detail)
      setView(nextView)
    } catch (err) {
      setError(err.message)
    }
  }

  async function refreshSelected(message) {
    setNotice(message)
    try {
      setSelected(await apiGet(`/books/${selected.id}`))
    } catch (err) {
      setError(err.message)
    }
    reload()
  }

  async function handleDelete(book) {
    const ok = window.confirm(`Xóa sách “${book.title}” cùng toàn bộ chương? Thao tác này không hoàn tác được.`)
    if (!ok) return
    setError('')
    setNotice('')
    try {
      await apiDelete(`/books/${book.id}`)
      setNotice(`Đã xóa sách “${book.title}”.`)
      // Xóa phần tử cuối của trang cuối thì lùi về trang trước
      if (result.content.length === 1 && page > 0) setPage(page - 1)
      else reload()
    } catch (err) {
      setError(err.message)
    }
  }

  if (view === 'create') {
    return (
      <BookForm
        onCancel={() => backToList()}
        onSaved={(saved) => backToList(`Đã tạo sách “${saved.title}”. Hãy thêm chương cho sách này.`)}
      />
    )
  }

  if (view === 'edit' && selected) {
    return (
      <BookForm
        initial={selected}
        onCancel={() => backToList()}
        onSaved={(saved) => backToList(`Đã cập nhật sách “${saved.title}”.`)}
      />
    )
  }

  if (view === 'chapters' && selected) {
    return (
      <>
        {notice && <p className="success-text" role="status">{notice}</p>}
        <ChapterManager
          book={selected}
          onBack={() => backToList()}
          onChanged={refreshSelected}
        />
      </>
    )
  }

  const books = result?.content ?? []

  return (
    <div>
      <div className="admin-head">
        <p className="muted">
          {result ? `${result.totalElements} sách trong kho` : 'Đang tải…'}
        </p>
        <button type="button" className="btn primary" onClick={() => { setNotice(''); setView('create') }}>
          + Thêm sách
        </button>
      </div>

      {notice && <p className="success-text" role="status">{notice}</p>}
      {error && <p className="error-text" role="alert">{error}</p>}

      <div className="table-wrap">
        <table className={`admin-table ${loading ? 'dimmed' : ''}`}>
          <thead>
            <tr>
              <th>Tên sách</th>
              <th>Tác giả</th>
              <th>Thể loại</th>
              <th>Chương</th>
              <th aria-label="Thao tác" />
            </tr>
          </thead>
          <tbody>
            {books.map((book) => (
              <tr key={book.id}>
                <td>{book.title}</td>
                <td>{book.author}</td>
                <td>{book.categories.join(', ')}</td>
                <td>{book.chapterCount}</td>
                <td className="row-actions">
                  <button type="button" className="btn small-btn" onClick={() => openBook(book.id, 'edit')}>Sửa</button>
                  <button type="button" className="btn small-btn" onClick={() => openBook(book.id, 'chapters')}>Chương</button>
                  <button type="button" className="btn danger small-btn" onClick={() => handleDelete(book)}>Xóa</button>
                </td>
              </tr>
            ))}
            {result && books.length === 0 && (
              <tr><td colSpan={5} className="muted">Chưa có sách nào.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {result && result.totalPages > 1 && (
        <div className="pager">
          <button type="button" className="btn" disabled={page === 0 || loading} onClick={() => setPage(page - 1)}>
            ← Trước
          </button>
          <span>Trang {result.page + 1} / {result.totalPages}</span>
          <button
            type="button"
            className="btn"
            disabled={page + 1 >= result.totalPages || loading}
            onClick={() => setPage(page + 1)}
          >
            Sau →
          </button>
        </div>
      )}
    </div>
  )
}

export function AdminPanel({ onBack }) {
  const { user, isAdmin, loading } = useAuth()

  return (
    <section className="panel">
      <button type="button" className="btn" onClick={onBack}>← Về kho sách</button>
      <h2>Quản trị kho sách</h2>

      {loading && <p className="muted">Đang kiểm tra quyền…</p>}
      {!loading && !user && (
        <p className="muted">Bạn cần đăng nhập bằng tài khoản quản trị ở tab “Tài khoản”.</p>
      )}
      {!loading && user && !isAdmin && (
        <p className="error-text">Tài khoản “{user.username}” không có quyền quản trị.</p>
      )}
      {!loading && isAdmin && <AdminBooks />}
    </section>
  )
}