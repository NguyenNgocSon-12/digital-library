export function IdentityPage() {
  return (
    <section className="panel">
      <h2>Tài khoản độc giả</h2>
      <p>Vũ xây API tài khoản, Sơn xây biểu mẫu đăng ký và đăng nhập sau khi nhóm chốt cơ chế xác thực.</p>
      <ul>
        <li>Đăng ký: <code>POST /api/users</code></li>
        <li>Đăng nhập: <code>POST /api/auth/login</code></li>
      </ul>
    </section>
  )
}
