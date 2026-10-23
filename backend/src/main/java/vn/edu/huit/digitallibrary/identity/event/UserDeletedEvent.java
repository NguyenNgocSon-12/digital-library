package vn.edu.huit.digitallibrary.identity.event;

/** Phát sau khi xóa độc giả khỏi MongoDB để domain khác dọn dữ liệu Redis tham chiếu userId. */
public record UserDeletedEvent(String userId) {
}
