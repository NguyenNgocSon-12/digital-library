package vn.edu.huit.digitallibrary.reading;

import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import vn.edu.huit.digitallibrary.catalog.service.BookService;
import vn.edu.huit.digitallibrary.identity.auth.CurrentUser;
import vn.edu.huit.digitallibrary.identity.model.Role;
import vn.edu.huit.digitallibrary.identity.service.UserService;
import vn.edu.huit.digitallibrary.reading.controller.ProgressController;
import vn.edu.huit.digitallibrary.reading.repository.ProgressRepository;
import vn.edu.huit.digitallibrary.reading.service.ProgressService;

@WebMvcTest(ProgressController.class)
@Import(ProgressService.class)
class ProgressApiTest {
    @Autowired MockMvc mvc;
    @MockitoBean ProgressRepository progress;
    @MockitoBean BookService books;
    @MockitoBean UserService users;

    @ParameterizedTest
    @ValueSource(strings = {
            "{}", "{\"chapter\":null,\"page\":1,\"line\":0}",
            "{\"chapter\":0,\"page\":1,\"line\":0}",
            "{\"chapter\":1,\"page\":0,\"line\":0}",
            "{\"chapter\":1,\"page\":1,\"line\":-1}",
            "{\"chapter\":\"wrong\",\"page\":1,\"line\":0}", "{",
            "{\"chapter\":1.5,\"page\":1,\"line\":0}",
            "{\"chapter\":1,\"page\":\"30\",\"line\":0}",
            "{\"chapter\":1,\"page\":1,\"line\":false}",
            "{\"chapter\":2147483648,\"page\":1,\"line\":0}"
    })
    void invalidBodiesNeverReachRedis(String body) throws Exception {
        login();
        mvc.perform(put("/api/progress/u1/b1").header("Authorization", "Bearer valid")
                        .contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("BAD_REQUEST"));
        verifyNoInteractions(progress, books);
    }

    @Test
    void missingAndInvalidTokensCannotReadOrWrite() throws Exception {
        mvc.perform(get("/api/progress/u1/b1")).andExpect(status().isUnauthorized());
        mvc.perform(put("/api/progress/u1/b1").header("Authorization", "Bearer invalid")
                .contentType(MediaType.APPLICATION_JSON).content("{\"chapter\":1,\"page\":1,\"line\":0}"))
                .andExpect(status().isUnauthorized());
        verifyNoInteractions(progress, books);
    }

    @Test
    void readerCannotAccessAnotherUsersProgress() throws Exception {
        login();
        mvc.perform(get("/api/progress/u2/b1").header("Authorization", "Bearer valid"))
                .andExpect(status().isForbidden());
        mvc.perform(put("/api/progress/u2/b1").header("Authorization", "Bearer valid")
                .contentType(MediaType.APPLICATION_JSON).content("{\"chapter\":1,\"page\":1,\"line\":0}"))
                .andExpect(status().isForbidden());
        verifyNoInteractions(progress, books);
    }

    private void login() {
        given(users.authenticate("valid")).willReturn(Optional.of(new CurrentUser("u1", "reader", Role.USER)));
    }
}
