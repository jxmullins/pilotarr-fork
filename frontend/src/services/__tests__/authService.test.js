import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock axios before importing authService (authService creates its own axios instance)
vi.mock("axios", () => {
  const mockClient = {
    post: vi.fn(),
    get: vi.fn(),
  };
  return {
    default: {
      create: vi.fn(() => mockClient),
    },
    __mockClient: mockClient,
  };
});

import axios from "axios";
import { loginApi, meApi, changePasswordApi } from "../authService";

const mockClient = axios.create();

beforeEach(() => {
  vi.clearAllMocks();
});

describe("loginApi", () => {
  it("posts credentials and returns response data", async () => {
    mockClient.post.mockResolvedValue({
      data: { access_token: "tok123", token_type: "bearer", username: "alice" },
    });

    const result = await loginApi("alice", "pass");

    expect(mockClient.post).toHaveBeenCalledWith("/auth/login", {
      username: "alice",
      password: "pass",
    });
    expect(result).toEqual({ access_token: "tok123", token_type: "bearer", username: "alice" });
  });

  it("throws on network error", async () => {
    mockClient.post.mockRejectedValue(new Error("Network Error"));
    await expect(loginApi("alice", "bad")).rejects.toThrow("Network Error");
  });
});

describe("meApi", () => {
  it("fetches /auth/me with Bearer header", async () => {
    mockClient.get.mockResolvedValue({ data: { username: "alice", is_active: true } });

    const result = await meApi("tok123");

    expect(mockClient.get).toHaveBeenCalledWith("/auth/me", {
      headers: { Authorization: "Bearer tok123" },
    });
    expect(result).toEqual({ username: "alice", is_active: true });
  });

  it("throws on 401", async () => {
    mockClient.get.mockRejectedValue({ response: { status: 401 } });
    await expect(meApi("bad-token")).rejects.toBeDefined();
  });
});

describe("changePasswordApi", () => {
  it("posts change-password with correct body and Bearer header", async () => {
    mockClient.post.mockResolvedValue({});

    await changePasswordApi("tok", "old", "newpass", "newpass");

    expect(mockClient.post).toHaveBeenCalledWith(
      "/auth/change-password",
      { current_password: "old", new_password: "newpass", confirm_password: "newpass" },
      { headers: { Authorization: "Bearer tok" } },
    );
  });

  it("throws on validation error", async () => {
    mockClient.post.mockRejectedValue({ response: { status: 422 } });
    await expect(changePasswordApi("tok", "old", "x", "y")).rejects.toBeDefined();
  });
});
