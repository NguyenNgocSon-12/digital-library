const API_BASE = '/api'
const TOKEN_KEY = 'dl_token'

export class ApiError extends Error {
  constructor(status, code, message) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // localStorage bị chặn: bỏ qua, phiên chỉ sống trong bộ nhớ
  }
}

async function request(method, path, body) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'NETWORK', 'Không kết nối được máy chủ. Hãy kiểm tra backend đã chạy chưa.')
  }

  if (response.status === 204) return null

  let data = null
  try {
    data = await response.json()
  } catch {
    // phản hồi không phải JSON
  }

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.code ?? 'ERROR',
      data?.message ?? `API trả về HTTP ${response.status}`,
    )
  }
  return data
}

export const apiGet = (path) => request('GET', path)
export const apiPost = (path, body) => request('POST', path, body ?? {})
export const apiPut = (path, body) => request('PUT', path, body ?? {})
export const apiDelete = (path) => request('DELETE', path)