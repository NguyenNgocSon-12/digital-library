import { useState } from 'react'
import { CatalogPage } from './features/catalog/CatalogPage'
import { IdentityPage } from './features/identity/IdentityPage'
import { RankingPage } from './features/ranking/RankingPage'
import { ReadingPage } from './features/reading/ReadingPage'
import { AuthProvider } from './shared/AuthProvider'
import { useAuth } from './shared/auth-context'
import { HealthBadge } from './shared/HealthBadge'

const pages = [
  { id: 'catalog', label: 'Kho sách', component: CatalogPage },
  { id: 'reading', label: 'Đọc sách', component: ReadingPage },
  { id: 'ranking', label: 'Thịnh hành', component: RankingPage },
  { id: 'identity', label: 'Tài khoản', component: IdentityPage },
]

function UserBox({ onLogin }) {
  const { user, isAdmin, loading, logout } = useAuth()

  if (loading) return <span className="muted small">Đang kiểm tra phiên…</span>

  if (!user) {
    return (
      <button type="button" className="btn" onClick={onLogin}>
        Đăng nhập
      </button>
    )
  }

  return (
    <div className="user-box">
      <span>
        {user.fullName || user.username}
        {isAdmin && <span className="badge">Admin</span>}
      </span>
      <button type="button" className="btn small-btn" onClick={logout}>
        Đăng xuất
      </button>
    </div>
  )
}

function Shell() {
  const [active, setActive] = useState('catalog')
  const CurrentPage = pages.find((page) => page.id === active).component

  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <span className="eyebrow">Đồ án NoSQL · MongoDB + Redis</span>
          <h1>Thư viện số</h1>
        </div>
        <div className="header-right">
          <HealthBadge />
          <UserBox onLogin={() => setActive('identity')} />
        </div>
      </header>
      <nav className="site-nav" aria-label="Chức năng chính">
        {pages.map((page) => (
          <button
            key={page.id}
            type="button"
            className={active === page.id ? 'active' : ''}
            onClick={() => setActive(page.id)}
            aria-current={active === page.id ? 'page' : undefined}
          >
            {page.label}
          </button>
        ))}
      </nav>
      <main><CurrentPage /></main>
      <footer>Đồ án NoSQL · Xem docs/SHARED.md để tích hợp API</footer>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  )
}