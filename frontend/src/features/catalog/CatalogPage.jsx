export function CatalogPage() {
  return (
    <section className="panel">
      <h2>Kho sách</h2>
      <p>Vũ sẽ cung cấp API MongoDB; Sơn ghép danh sách, tìm kiếm, chi tiết sách và giao diện quản trị tại đây.</p>
      <ul>
        <li>Danh sách sách: <code>GET /api/books</code></li>
        <li>Chi tiết và chương: <code>GET /api/books/:bookId</code></li>
        <li>Thao tác quản trị được thống nhất trong <code>docs/SHARED.md</code></li>
      </ul>
    </section>
  )
}
