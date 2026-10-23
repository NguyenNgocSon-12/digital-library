import { useState } from 'react'
import { useAuth } from '../../shared/auth-context'
import { AdminPanel } from './AdminPanel'
import { BookDetail } from './BookDetail'
import { BookList } from './BookList'

export function CatalogPage() {
  const { isAdmin } = useAuth()
  const [view, setView] = useState('list') // list | detail | admin
  const [bookId, setBookId] = useState(null)
  // Tăng sau khi vào trang quản trị để danh sách tải lại dữ liệu mới
  const [listVersion, setListVersion] = useState(0)

  function openBook(id) {
    setBookId(id)
    setView('detail')
  }

  function backToList() {
    setView('list')
  }

  function leaveAdmin() {
    setListVersion((v) => v + 1)
    setView('list')
  }

  if (view === 'admin') {
    return <AdminPanel onBack={leaveAdmin} />
  }

  return (
    <>
      {/* Giữ BookList luôn được mount để khi quay lại vẫn còn từ khóa, thể loại, trang đang xem */}
      <div hidden={view !== 'list'}>
        {isAdmin && (
          <div className="admin-bar">
            <button type="button" className="btn" onClick={() => setView('admin')}>
              Quản trị kho sách
            </button>
          </div>
        )}
        <BookList key={listVersion} onSelect={openBook} />
      </div>

      {view === 'detail' && <BookDetail bookId={bookId} onBack={backToList} />}
    </>
  )
}