export function RankingPage() {
  return (
    <section className="panel">
      <h2>Sách thịnh hành</h2>
      <p>Đạt cung cấp thứ hạng từ Redis ZSET; Sơn hiển thị và ghép dữ liệu sách từ MongoDB.</p>
      <ul><li>Top sách: <code>GET /api/ranking?top=10</code></li></ul>
    </section>
  )
}
