import { useState } from 'react'
import { CatalogPage } from './features/catalog/CatalogPage'
import { IdentityPage } from './features/identity/IdentityPage'
import { RankingPage } from './features/ranking/RankingPage'
import { ReadingPage } from './features/reading/ReadingPage'
import { HealthBadge } from './shared/HealthBadge'

const pages = [
  { id: 'catalog', label: 'Kho sách', component: CatalogPage },
  { id: 'reading', label: 'Đọc sách', component: ReadingPage },
  { id: 'ranking', label: 'Thịnh hành', component: RankingPage },
  { id: 'identity', label: 'Tài khoản', component: IdentityPage },
]

export default function App() {
  const [active, setActive] = useState('catalog')
  const CurrentPage = pages.find((page) => page.id === active).component

  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <span className="eyebrow">Đồ án NoSQL · MongoDB + Redis</span>
          <h1>Thư viện số</h1>
        </div>
        <HealthBadge />
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
      <footer>Khung giao diện React · Xem docs/SHARED.md để tích hợp API</footer>
    </div>
  )
}
