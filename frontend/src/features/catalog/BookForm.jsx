import { useState } from 'react'
import { apiPost, apiPut } from '../../shared/api'

function parseCategories(text) {
  const unique = new Set(
    text.split(',').map((item) => item.trim()).filter(Boolean),
  )
  return [...unique]
}

/**
 * initial = null  -> thêm sách mới (POST /books)
 * initial = BookDetail -> sửa thông tin sách (PUT /books/{id}), không đụng tới chương
 */
export function BookForm({ initial = null, onSaved, onCancel }) {
  const isEdit = Boolean(initial)
  const [form, setForm] = useState({
    title: initial?.title ?? '',
    author: initial?.author ?? '',
    categories: initial?.categories?.join(', ') ?? '',
    description: initial?.description ?? '',
    coverUrl: initial?.coverUrl ?? '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const update = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))

  function validate(categories) {
    if (!form.title.trim()) return 'Vui lòng nhập tên sách.'
    if (form.title.trim().length > 300) return 'Tên sách tối đa 300 ký tự.'
    if (!form.author.trim()) return 'Vui lòng nhập tác giả.'
    if (form.author.trim().length > 200) return 'Tên tác giả tối đa 200 ký tự.'
    if (categories.length > 20) return 'Tối đa 20 thể loại.'
    if (categories.some((name) => name.length > 100)) return 'Mỗi thể loại tối đa 100 ký tự.'
    if (form.description.length > 5000) return 'Mô tả tối đa 5000 ký tự.'
    if (form.coverUrl.length > 2000) return 'Đường dẫn ảnh bìa tối đa 2000 ký tự.'
    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const categories = parseCategories(form.categories)
    const problem = validate(categories)
    if (problem) {
      setError(problem)
      return
    }

    const payload = {
      title: form.title.trim(),
      author: form.author.trim(),
      categories,
      description: form.description.trim(),
      coverUrl: form.coverUrl.trim(),
    }

    setError('')
    setBusy(true)
    try {
      const saved = isEdit
        ? await apiPut(`/books/${initial.id}`, payload)
        : await apiPost('/books', { ...payload, chapters: [] })
      onSaved(saved)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h3>{isEdit ? 'Sửa thông tin sách' : 'Thêm sách mới'}</h3>

      <label className="field">
        <span>Tên sách *</span>
        <input value={form.title} onChange={update('title')} maxLength={300} required />
      </label>
      <label className="field">
        <span>Tác giả *</span>
        <input value={form.author} onChange={update('author')} maxLength={200} required />
      </label>
      <label className="field">
        <span>Thể loại (cách nhau bằng dấu phẩy)</span>
        <input
          value={form.categories}
          onChange={update('categories')}
          placeholder="Văn học, Thiếu nhi"
        />
      </label>
      <label className="field">
        <span>Mô tả</span>
        <textarea value={form.description} onChange={update('description')} rows={4} maxLength={5000} />
      </label>
      <label className="field">
        <span>Đường dẫn ảnh bìa</span>
        <input
          type="url"
          value={form.coverUrl}
          onChange={update('coverUrl')}
          placeholder="https://…"
        />
      </label>

      {isEdit && (
        <p className="muted small">
          Form này chỉ sửa thông tin sách. Để thêm hoặc sửa chương, dùng mục “Chương” trong trang quản trị.
        </p>
      )}
      {error && <p className="error-text" role="alert">{error}</p>}

      <div className="form-actions">
        <button type="submit" className="btn primary" disabled={busy}>
          {busy ? 'Đang lưu…' : isEdit ? 'Lưu thay đổi' : 'Tạo sách'}
        </button>
        <button type="button" className="btn" onClick={onCancel} disabled={busy}>Hủy</button>
      </div>
    </form>
  )
}