package vn.edu.huit.digitallibrary.catalog.event;

/** Phát sau khi xóa sách khỏi MongoDB để domain khác dọn dữ liệu Redis tham chiếu bookId. */
public record BookDeletedEvent(String bookId) {
}
