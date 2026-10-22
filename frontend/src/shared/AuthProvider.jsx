import { useCallback, useEffect, useMemo, useState } from 'react'
import { apiGet, apiPost, getToken, setToken } from './api'
import { AuthContext } from './auth-context'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // Chỉ "đang tải" khi có token cần xác minh với backend
  const [loading, setLoading] = useState(() => Boolean(getToken()))

  // Khôi phục phiên khi tải lại trang: hỏi GET /api/auth/me bằng token đã lưu
  useEffect(() => {
    if (!getToken()) return undefined
    let active = true
    apiGet('/auth/me')
      .then((me) => { if (active) setUser(me) })
      .catch(() => setToken(null)) // token hết hạn hoặc sai: bỏ đi
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const login = useCallback(async (username, password) => {
    const result = await apiPost('/auth/login', { username, password })
    setToken(result.token)
    setUser(result.user)
    return result.user
  }, [])

  const register = useCallback(
    (payload) => apiPost('/users', payload),
    [],
  )

  const logout = useCallback(async () => {
    try {
      await apiPost('/auth/logout')
    } catch {
      // token đã hết hạn hoặc mất mạng: vẫn đăng xuất phía client
    }
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, isAdmin: user?.role === 'ADMIN', loading, login, register, logout }),
    [user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}