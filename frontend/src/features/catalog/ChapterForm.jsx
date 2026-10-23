import { useState } from 'react'
import { apiPost } from '../../shared/api'

const emptySection = () => ({ heading: '', text: '' })

export function ChapterForm({ book, onSaved, onCancel }) {
  const [chapterNo, setChapterNo] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [sections, setSections] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const nextNo = book.chapters.length
    ? Math.max(...book.chapters.map((c) => c.chapterNo)) + 1
    : 1

  function updateSection(index, field, value) {
    setSections((prev) => prev.map((s, i) => (i === index ? { ...s, [field]: value } : s)))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!title.trim()) {
      setError('Vui lòng nhập tiêu đề chương.')
      return
    }
    if (title.trim().length > 300) {
      setError('Tiêu đề chương tối đa 300 ký tự.')
      return
    }
    let number = null
    if (chapterNo.trim() !== '') {
      number = Number(chapterNo)
      if (!Number.isInteger(number) || number < 1) {
        setError('Số chương phải là số nguyên từ 1 trở lên.')
        return
      }
    }
    const cleanSections = sections.filter((s) => s.heading.trim() || s.text.trim())
    if (cleanSections.some((s) => s.heading.trim().length > 300)) {
      setError('Tiêu đề mục tối đa 300 ký tự.')
      return
    }

    const payload = {
      title: title.trim(),
      content,
      sections: cleanSections.map((s) => ({ heading: s.heading.trim(), text: s.text })),
    }
    if (number !== null) payload.chapterNo = number

    setError('')
    setBusy(true)
    try {
      const saved = await apiPost(`/books/${book.id}/chapters`, payload)
      onSaved(saved)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h3>Thêm chương cho “{book.title}”</h3>

      <label className="field">
        <span>Số chương (để trống sẽ tự gán số {nextNo})</span>
        <input
          type="number"
          min="1"
          step="1"
          value={chapterNo}
          onChange={(e) => setChapterNo(e.target.value)}
          placeholder={String(nextNo)}
        />
      </label>
      <label className="field">
        <span>Tiêu đề chương *</span>
        <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={300} required />
      </label>
      <label className="field">
        <span>Nội dung chương</span>
        <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={8} />
      </label>

      <fieldset className="sections">
        <legend>Các mục trong chương (không bắt buộc)</legend>
        {sections.map((section, index) => (
          <div key={index} className="section-row">
            <label className="field">
              <span>Tiêu đề mục {index + 1}</span>
              <input
                value={section.heading}
                onChange={(e) => updateSection(index, 'heading', e.target.value)}
                maxLength={300}
              />
            </label>
            <label className="field">
              <span>Nội dung mục {index + 1}</span>
              <textarea
                value={section.text}
                onChange={(e) => updateSection(index, 'text', e.target.value)}
                rows={3}
              />
            </label>
            <button
              type="button"
              className="btn danger small-btn"
              onClick={() => setSections((prev) => prev.filter((_, i) => i !== index))}
            >
              Xóa mục
            </button>
          </div>
        ))}
        <button
          type="button"
          className="btn"
          onClick={() => setSections((prev) => [...prev, emptySection()])}
        >
          + Thêm mục
        </button>
      </fieldset>

      {error && <p className="error-text" role="alert">{error}</p>}

      <div className="form-actions">
        <button type="submit" className="btn primary" disabled={busy}>
          {busy ? 'Đang lưu…' : 'Thêm chương'}
        </button>
        <button type="button" className="btn" onClick={onCancel} disabled={busy}>Hủy</button>
      </div>
    </form>
  )
}