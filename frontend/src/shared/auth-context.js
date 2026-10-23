import { createContext, useContext } from 'react'

/**
 * Giá trị context:
 *  - user:     UserResponse hoặc null (chưa đăng nhập)
 *  - isAdmin:  true nếu user.role === 'ADMIN'
 *  - loading:  true khi đang khôi phục phiên từ token đã lưu
 *  - login(username, password): đăng nhập, ném ApiError nếu sai
 *  - register(payload):         đăng ký (role USER), không tự đăng nhập
 *  - logout():                  đăng xuất, luôn xóa phiên phía client
 */
export const AuthContext = createContext(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth phải được dùng bên trong <AuthProvider>')
  }
  return context
}