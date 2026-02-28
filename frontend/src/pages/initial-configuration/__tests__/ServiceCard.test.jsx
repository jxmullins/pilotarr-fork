import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

import ServiceCard from "../components/ServiceCard";

const baseService = {
  id: "radarr",
  name: "Radarr",
  icon: "Film",
  description: "Movie collection manager",
  url: "",
  apiKey: "",
  port: "7878",
  hasApiKey: false,
  hasPassword: false,
};

const qbService = {
  id: "qbittorrent",
  name: "qBittorrent",
  icon: "Download",
  description: "Torrent client",
  url: "",
  username: "",
  password: "",
  port: "8080",
  hasApiKey: false,
  hasPassword: false,
};

const renderCard = (props = {}) => {
  const onTest = props.onTest ?? vi.fn();
  const onConfigChange = props.onConfigChange ?? vi.fn();
  return render(
    <ServiceCard
      service={props.service ?? baseService}
      onTest={onTest}
      onConfigChange={onConfigChange}
      testStatus={props.testStatus ?? null}
    />,
  );
};

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe("ServiceCard – rendering (API service)", () => {
  it("shows service name and description", () => {
    renderCard();
    expect(screen.getByText("Radarr")).toBeInTheDocument();
    expect(screen.getByText("Movie collection manager")).toBeInTheDocument();
  });

  it("renders a URL input", () => {
    renderCard();
    expect(screen.getByPlaceholderText("https://example.com")).toBeInTheDocument();
  });

  it("renders an API key field (not username/password)", () => {
    renderCard();
    expect(screen.getByText("API Key")).toBeInTheDocument();
    expect(screen.queryByText("Username")).not.toBeInTheDocument();
  });

  it("shows 'Not Tested' status when no testStatus is provided", () => {
    renderCard();
    expect(screen.getByText("Not Tested")).toBeInTheDocument();
  });

  it("Test Connection button is disabled when URL and API key are empty", () => {
    renderCard();
    expect(screen.getByRole("button", { name: /test connection/i })).toBeDisabled();
  });
});

describe("ServiceCard – rendering (qBittorrent)", () => {
  it("shows username and password fields instead of API key", () => {
    renderCard({ service: qbService });
    expect(screen.getByText("Username")).toBeInTheDocument();
    expect(screen.getByText("Password")).toBeInTheDocument();
    expect(screen.queryByText("API Key")).not.toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Status display
// ---------------------------------------------------------------------------

describe("ServiceCard – test status display", () => {
  it("shows 'Connected' on success status", () => {
    renderCard({ testStatus: { status: "success", message: "Connection successful" } });
    expect(screen.getByText("Connected")).toBeInTheDocument();
    expect(screen.getByText("Connection successful")).toBeInTheDocument();
  });

  it("shows 'Failed' on error status", () => {
    renderCard({
      testStatus: { status: "error", message: "Connection failed", details: "Timeout" },
    });
    expect(screen.getByText("Failed")).toBeInTheDocument();
    expect(screen.getByText("Connection failed")).toBeInTheDocument();
    expect(screen.getByText("Timeout")).toBeInTheDocument();
  });

  it("shows 'Testing...' on testing status", () => {
    renderCard({ testStatus: { status: "testing", message: "Testing connection..." } });
    expect(screen.getByText("Testing...")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Interactions
// ---------------------------------------------------------------------------

describe("ServiceCard – interactions", () => {
  it("calls onConfigChange when URL is typed", async () => {
    const user = userEvent.setup();
    const onConfigChange = vi.fn();
    renderCard({ onConfigChange });

    await user.type(screen.getByPlaceholderText("https://example.com"), "http://localhost:7878");

    await waitFor(() => expect(onConfigChange).toHaveBeenCalled());
    const lastCall = onConfigChange.mock.calls.at(-1);
    expect(lastCall[0]).toBe("radarr");
    expect(lastCall[1].url).toBe("http://localhost:7878");
  });

  it("enables Test Connection button when URL and API key are filled", async () => {
    const user = userEvent.setup();
    renderCard();

    await user.type(screen.getByPlaceholderText("https://example.com"), "http://localhost:7878");
    // API key input placeholder
    await user.type(screen.getByPlaceholderText("Enter your API key"), "my-api-key");

    expect(screen.getByRole("button", { name: /test connection/i })).not.toBeDisabled();
  });

  it("calls onTest with serviceId and config when Test Connection is clicked", async () => {
    const user = userEvent.setup();
    const onTest = vi.fn();
    renderCard({ onTest });

    await user.type(screen.getByPlaceholderText("https://example.com"), "http://localhost:7878");
    await user.type(screen.getByPlaceholderText("Enter your API key"), "my-api-key");
    await user.click(screen.getByRole("button", { name: /test connection/i }));

    expect(onTest).toHaveBeenCalledWith(
      "radarr",
      expect.objectContaining({ url: "http://localhost:7878", apiKey: "my-api-key" }),
    );
  });

  it("disables Test Connection button while testing", () => {
    renderCard({ testStatus: { status: "testing", message: "Testing..." } });
    expect(screen.getByRole("button", { name: /test connection/i })).toBeDisabled();
  });

  it("toggles API key visibility", async () => {
    const user = userEvent.setup();
    renderCard();

    const apiKeyInput = screen.getByPlaceholderText("Enter your API key");
    expect(apiKeyInput).toHaveAttribute("type", "password");

    await user.click(screen.getByRole("button", { name: /show api key/i }));
    expect(apiKeyInput).toHaveAttribute("type", "text");

    await user.click(screen.getByRole("button", { name: /hide api key/i }));
    expect(apiKeyInput).toHaveAttribute("type", "password");
  });

  it("toggles password visibility for qBittorrent", async () => {
    const user = userEvent.setup();
    renderCard({ service: qbService });

    const passwordInput = screen.getByPlaceholderText("Enter your password");
    expect(passwordInput).toHaveAttribute("type", "password");

    await user.click(screen.getByRole("button", { name: /show password/i }));
    expect(passwordInput).toHaveAttribute("type", "text");
  });

  it("shows encryption notice when apiKey is present", async () => {
    const user = userEvent.setup();
    renderCard();

    await user.type(screen.getByPlaceholderText("Enter your API key"), "secret");
    expect(screen.getByText(/api key.*will be encrypted/i)).toBeInTheDocument();
  });

  it("enables Test Connection for qBittorrent when URL + username + password filled", async () => {
    const user = userEvent.setup();
    renderCard({ service: qbService });

    await user.type(screen.getByPlaceholderText("https://example.com"), "http://localhost:8080");
    await user.type(screen.getByPlaceholderText("Enter your username"), "admin");
    await user.type(screen.getByPlaceholderText("Enter your password"), "pass");

    expect(screen.getByRole("button", { name: /test connection/i })).not.toBeDisabled();
  });
});

// ---------------------------------------------------------------------------
// hasApiKey / hasPassword flags (saved credentials)
// ---------------------------------------------------------------------------

describe("ServiceCard – saved credential hints", () => {
  it("shows placeholder hint when API key is already saved", () => {
    renderCard({ service: { ...baseService, hasApiKey: true } });
    expect(screen.getByPlaceholderText("Saved — enter new value to change")).toBeInTheDocument();
  });

  it("enables Test Connection when hasApiKey is true (no new key required)", async () => {
    const user = userEvent.setup();
    renderCard({ service: { ...baseService, url: "http://localhost:7878", hasApiKey: true } });

    // URL is pre-filled, hasApiKey means valid — button should be enabled
    expect(screen.getByRole("button", { name: /test connection/i })).not.toBeDisabled();
  });
});
