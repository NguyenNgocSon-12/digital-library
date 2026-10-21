const API_BASE = '/api'

export async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`API trả về HTTP ${response.status}`)
  }
  return response.json()
}
