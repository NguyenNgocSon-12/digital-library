import { useEffect, useState } from 'react'
import { apiGet } from './api'

export function HealthBadge() {
  const [online, setOnline] = useState(false)

  useEffect(() => {
    let mounted = true
    apiGet('/health')
      .then(() => { if (mounted) setOnline(true) })
      .catch(() => { if (mounted) setOnline(false) })
    return () => { mounted = false }
  }, [])

  return (
    <span className={`health ${online ? 'online' : ''}`}>
      API {online ? 'đang chạy' : 'chưa kết nối'}
    </span>
  )
}
