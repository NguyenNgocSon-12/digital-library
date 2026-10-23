import { useState } from 'react'
import { useAuth } from '../../shared/auth-context'

const USERNAME_PATTERN = /^[A-Za-z0-9_.]{3,32}$/
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function LoginForm({ onSuccess }) {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(username.trim(), password)
      onSuccess?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label className="field">
        <span>Tên đăng nhập</span>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />
      </label>
      <label className="field">
        <span>Mật khẩu</span>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </label>
      {error && <p className="error-text" role="alert">{error}</p>}
      <button type="submit" className="btn primary" disabled={busy}>
        {busy ? 'Đang đăng nhập…' : 'Đăng nhập'}
      </button>
    </form>
  )
}

function RegisterForm({ onRegistered }) {
  const { register } = useAuth()
  const [form, setForm] = useState({ username: '', email: '', fullName: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const update = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))

  function validate() {
    if (!USERNAME_PATTERN.test(form.username.trim())) {
      return 'Tên đăng nhập chỉ gồm chữ, số, dấu _ hoặc . và dài 3–32 ký tự.'
    }
    if (!EMAIL_PATTERN.test(form.email.trim())) return 'Email không hợp lệ.'
    if (form.fullName.length > 100) return 'Họ tên tối đa 100 ký tự.'
    if (form.password.length < 6 || form.password.length > 72) {
      return 'Mật khẩu phải dài 6–72 ký tự.'
    }
    if (form.password !== form.confirm) return 'Mật khẩu nhập lại không khớp.'
    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const problem = validate()
    if (problem) {
      setError(problem)
      return
    }
    setError('')
    setBusy(true)
    try {
      await register({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        fullName: form.fullName.trim() || null,
      })
      onRegistered(form.username.trim())
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label className="field">
        <span>Tên đăng nhập</span>
        <input value={form.username} onChange={update('username')} autoComplete="username" required />
      </label>
      <label className="field">
        <span>Email</span>
        <input type="email" value={form.email} onChange={update('email')} autoComplete="email" required />
      </label>
      <label className="field">
        <span>Họ và tên (không bắt buộc)</span>
        <input value={form.fullName} onChange={update('fullName')} autoComplete="name" maxLength={100} />
      </label>
      <label className="field">
        <span>Mật khẩu</span>
        <input type="password" value={form.password} onChange={update('password')} autoComplete="new-password" required />
      </label>
      <label className="field">
        <span>Nhập lại mật khẩu</span>
        <input type="password" value={form.confirm} onChange={update('confirm')} autoComplete="new-password" required />
      </label>
      {error && <p className="error-text" role="alert">{error}</p>}
      <button type="submit" className="btn primary" disabled={busy}>
        {busy ? 'Đang đăng ký…' : 'Đăng ký'}
      </button>
    </form>
  )
}

function AccountInfo() {
  const { user, isAdmin, logout } = useAuth()
  return (
    <>
      <h2>Xin chào, {user.fullName || user.username}</h2>
      <dl className="info-list">
        <dt>Tên đăng nhập</dt>
        <dd>{user.username}</dd>
        <dt>Email</dt>
        <dd>{user.email}</dd>
        <dt>Vai trò</dt>
        <dd>{isAdmin ? 'Quản trị viên' : 'Độc giả'}</dd>
        <dt>Ngày tạo</dt>
        <dd>{new Date(user.createdAt).toLocaleString('vi-VN')}</dd>
      </dl>
      <button type="button" className="btn" onClick={logout}>Đăng xuất</button>
    </>
  )
}

export function IdentityPage() {
  const { user, loading } = useAuth()
  const [mode, setMode] = useState('login')
  const [notice, setNotice] = useState('')

  if (loading) {
    return <section className="panel narrow"><p>Đang kiểm tra phiên đăng nhập…</p></section>
  }

  if (user) {
    return <section className="panel narrow"><AccountInfo /></section>
  }

  return (
    <section className="panel narrow">
      <div className="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'login'}
          className={mode === 'login' ? 'active' : ''}
          onClick={() => { setMode('login'); setNotice('') }}
        >
          Đăng nhập
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'register'}
          className={mode === 'register' ? 'active' : ''}
          onClick={() => { setMode('register'); setNotice('') }}
        >
          Đăng ký
        </button>
      </div>

      {notice && <p className="success-text" role="status">{notice}</p>}

      {mode === 'login' ? (
        <LoginForm />
      ) : (
        <RegisterForm
          onRegistered={(username) => {
            setNotice(`Đăng ký thành công. Hãy đăng nhập bằng tài khoản "${username}".`)
            setMode('login')
          }}
        />
      )}
    </section>
  )
}