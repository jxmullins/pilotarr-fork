import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "../AuthContext";

// Mock the authService module
vi.mock("../../services/authService", () => ({
  loginApi: vi.fn(),
  meApi: vi.fn(),
  changePasswordApi: vi.fn(),
}));

import { loginApi, meApi, changePasswordApi } from "../../services/authService";

// Helper component to expose context values
const AuthConsumer = () => {
  const { user, isAuthenticated, initializing } = useAuth();
  return (
    <div>
      <span data-testid="user">{user?.username ?? "none"}</span>
      <span data-testid="auth">{String(isAuthenticated)}</span>
      <span data-testid="init">{String(initializing)}</span>
    </div>
  );
};

const renderWithAuth = (ui = <AuthConsumer />) => render(<AuthProvider>{ui}</AuthProvider>);

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("AuthProvider – initial state", () => {
  it("starts unauthenticated when no token in localStorage", async () => {
    meApi.mockRejectedValue(new Error("no token"));
    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("init").textContent).toBe("false"));
    expect(screen.getByTestId("auth").textContent).toBe("false");
    expect(screen.getByTestId("user").textContent).toBe("none");
  });

  it("restores session from valid localStorage token", async () => {
    localStorage.setItem("pilotarr_token", "valid-tok");
    meApi.mockResolvedValue({ username: "alice", is_active: true });
    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("init").textContent).toBe("false"));
    expect(screen.getByTestId("auth").textContent).toBe("true");
    expect(screen.getByTestId("user").textContent).toBe("alice");
  });

  it("clears invalid token from localStorage on restore failure", async () => {
    localStorage.setItem("pilotarr_token", "expired-tok");
    meApi.mockRejectedValue({ response: { status: 401 } });
    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("init").textContent).toBe("false"));
    expect(localStorage.getItem("pilotarr_token")).toBeNull();
    expect(screen.getByTestId("auth").textContent).toBe("false");
  });
});

describe("login()", () => {
  const LoginTester = () => {
    const { login, user, isAuthenticated } = useAuth();
    return (
      <div>
        <span data-testid="user">{user?.username ?? "none"}</span>
        <span data-testid="auth">{String(isAuthenticated)}</span>
        <button onClick={() => login("alice", "pass")}>login</button>
        <button onClick={() => login("alice", "bad")}>bad-login</button>
      </div>
    );
  };

  it("sets user and persists token on success", async () => {
    meApi.mockRejectedValue(new Error("no stored token"));
    loginApi.mockResolvedValue({ access_token: "tok123", username: "alice" });
    render(
      <AuthProvider>
        <LoginTester />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("auth").textContent).toBe("false"));

    await act(() => screen.getByText("login").click());

    expect(screen.getByTestId("user").textContent).toBe("alice");
    expect(screen.getByTestId("auth").textContent).toBe("true");
    expect(localStorage.getItem("pilotarr_token")).toBe("tok123");
  });

  it("returns { ok: false } with error message on failure", async () => {
    meApi.mockRejectedValue(new Error("no stored token"));
    loginApi.mockRejectedValue({ response: { data: { detail: "Invalid credentials" } } });
    let result;
    const Capture = () => {
      const { login } = useAuth();
      return (
        <button
          onClick={async () => {
            result = await login("x", "y");
          }}
        >
          go
        </button>
      );
    };
    render(
      <AuthProvider>
        <Capture />
      </AuthProvider>,
    );
    await act(() => screen.getByText("go").click());
    expect(result).toEqual({ ok: false, error: "Invalid credentials" });
  });
});

describe("logout()", () => {
  it("clears user and removes token from localStorage", async () => {
    localStorage.setItem("pilotarr_token", "tok");
    meApi.mockResolvedValue({ username: "alice", is_active: true });
    const LogoutTester = () => {
      const { logout, isAuthenticated } = useAuth();
      return (
        <div>
          <span data-testid="auth">{String(isAuthenticated)}</span>
          <button onClick={logout}>logout</button>
        </div>
      );
    };
    render(
      <AuthProvider>
        <LogoutTester />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("auth").textContent).toBe("true"));

    await act(() => screen.getByText("logout").click());

    expect(screen.getByTestId("auth").textContent).toBe("false");
    expect(localStorage.getItem("pilotarr_token")).toBeNull();
  });
});

describe("changePassword()", () => {
  it("returns { ok: true } on success", async () => {
    meApi.mockResolvedValue({ username: "alice", is_active: true });
    localStorage.setItem("pilotarr_token", "tok");
    changePasswordApi.mockResolvedValue({});
    let result;
    const Tester = () => {
      const { changePassword } = useAuth();
      return (
        <button
          onClick={async () => {
            result = await changePassword("old", "new1", "new1");
          }}
        >
          go
        </button>
      );
    };
    render(
      <AuthProvider>
        <Tester />
      </AuthProvider>,
    );
    await waitFor(() => {});
    await act(() => screen.getByText("go").click());
    expect(result).toEqual({ ok: true });
  });

  it("returns { ok: false } with error on failure", async () => {
    meApi.mockRejectedValue(new Error("no token"));
    changePasswordApi.mockRejectedValue({ response: { data: { detail: "Wrong password" } } });
    let result;
    const Tester = () => {
      const { changePassword } = useAuth();
      return (
        <button
          onClick={async () => {
            result = await changePassword("wrong", "new", "new");
          }}
        >
          go
        </button>
      );
    };
    render(
      <AuthProvider>
        <Tester />
      </AuthProvider>,
    );
    await waitFor(() => {});
    await act(() => screen.getByText("go").click());
    expect(result).toEqual({ ok: false, error: "Wrong password" });
  });
});
