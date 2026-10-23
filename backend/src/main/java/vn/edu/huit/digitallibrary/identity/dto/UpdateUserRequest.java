package vn.edu.huit.digitallibrary.identity.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

/** Trường nào null thì giữ nguyên. */
public record UpdateUserRequest(
        @Email @Size(max = 254) @Pattern(regexp = "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
                message = "phải có dạng ten@mien.tld") String email,
        @Size(max = 100) String fullName,
        @Size(min = 6, max = 72) String password) {
}
