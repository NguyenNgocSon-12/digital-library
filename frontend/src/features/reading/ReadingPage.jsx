export function ReadingPage() {
  return (
    <section className="panel">
      <h2>Trình đọc sách</h2>
      <p>Sơn xây giao diện đọc, khôi phục trang đang đọc và lưu tiến trình qua API Redis do Đạt phụ trách.</p>
      <ul>
        <li>Lấy tiến trình: <code>GET /api/progress/:userId/:bookId</code></li>
        <li>Lưu tiến trình: <code>PUT /api/progress/:userId/:bookId</code></li>
        <li>Mở chương: <code>POST /api/books/:bookId/read</code></li>
      </ul>
    </section>
  )
}
