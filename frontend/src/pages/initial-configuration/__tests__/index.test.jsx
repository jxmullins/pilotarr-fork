import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

// --- Mocks ---

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("../../../components/navigation/Header", () => ({
  default: () => <header data-testid="header" />,
}));

vi.mock("../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

const mockGetServiceConfigurations = vi.fn();
const mockSaveServiceConfiguration = vi.fn();
const mockTestServiceConnection = vi.fn();

vi.mock("../../../services/configService", () => ({
  getServiceConfigurations: (...args) => mockGetServiceConfigurations(...args),
  saveServiceConfiguration: (...args) => mockSaveServiceConfiguration(...args),
  testServiceConnection: (...args) => mockTestServiceConnection(...args),
}));

import InitialConfiguration from "../index";

const renderPage = () =>
  render(
    <MemoryRouter>
      <InitialConfiguration />
    </MemoryRouter>,
  );

beforeEach(() => {
  vi.clearAllMocks();
  mockGetServiceConfigurations.mockResolvedValue([]);
  mockSaveServiceConfiguration.mockResolvedValue({});
});

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe("InitialConfiguration – rendering", () => {
  it("shows a loading spinner while configurations are being fetched", () => {
    // Never resolves during this test
    mockGetServiceConfigurations.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading configurations/i)).toBeInTheDocument();
  });

  it("renders the page heading after loading", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /initial configuration/i })).toBeInTheDocument(),
    );
  });

  it("renders all 6 service cards after loading", async () => {
    renderPage();
    // Each name appears in both the ServiceCard header and the ConfigurationProgress tile
    await waitFor(() => {
      expect(screen.getAllByText("Radarr").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Sonarr").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Jellyfin").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Jellyseerr").length).toBeGreaterThan(0);
      expect(screen.getAllByText("qBittorrent").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Prowlarr").length).toBeGreaterThan(0);
    });
  });

  it("renders the Save All Configurations button", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /save all configurations/i })).toBeInTheDocument(),
    );
  });

  it("renders the Configuration Progress section", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText(/configuration progress/i)).toBeInTheDocument());
  });
});

// ---------------------------------------------------------------------------
// Loading existing configurations
// ---------------------------------------------------------------------------

describe("InitialConfiguration – loading saved data", () => {
  it("pre-fills URL from saved configuration", async () => {
    mockGetServiceConfigurations.mockResolvedValue([
      {
        serviceName: "radarr",
        url: "http://192.168.1.10:7878",
        port: "7878",
        hasApiKey: true,
        hasPassword: false,
        testStatus: null,
      },
    ]);

    renderPage();

    await waitFor(() => {
      const inputs = screen.getAllByDisplayValue("http://192.168.1.10:7878");
      expect(inputs.length).toBeGreaterThan(0);
    });
  });

  it("restores test status badge from saved data", async () => {
    mockGetServiceConfigurations.mockResolvedValue([
      {
        serviceName: "radarr",
        url: "http://192.168.1.10:7878",
        port: "7878",
        hasApiKey: true,
        hasPassword: false,
        testStatus: "success",
        testMessage: "Connected",
      },
    ]);

    renderPage();

    await waitFor(() => {
      // "Connected" appears in the service card status
      expect(screen.getAllByText("Connected").length).toBeGreaterThan(0);
    });
  });

  it("handles API errors gracefully and still renders the page", async () => {
    mockGetServiceConfigurations.mockRejectedValue(new Error("Network error"));
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /initial configuration/i })).toBeInTheDocument(),
    );
  });
});

// ---------------------------------------------------------------------------
// Save behaviour
// ---------------------------------------------------------------------------

describe("InitialConfiguration – save", () => {
  it("calls saveServiceConfiguration only for services with a URL", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /save all configurations/i })).toBeInTheDocument(),
    );

    // Type a URL into the first service URL input (Radarr)
    const urlInputs = screen.getAllByPlaceholderText("https://example.com");
    await user.type(urlInputs[0], "http://localhost:7878");

    await user.click(screen.getByRole("button", { name: /save all configurations/i }));

    await waitFor(() => expect(mockSaveServiceConfiguration).toHaveBeenCalledTimes(1));
    expect(mockSaveServiceConfiguration).toHaveBeenCalledWith(
      "radarr",
      expect.objectContaining({ url: "http://localhost:7878" }),
    );
  });

  it("shows success banner after saving", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /save all configurations/i })).toBeInTheDocument(),
    );

    await user.click(screen.getByRole("button", { name: /save all configurations/i }));

    await waitFor(() =>
      expect(screen.getByText(/configuration saved successfully/i)).toBeInTheDocument(),
    );
  });

  it("redirects to /main-dashboard after save success", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /save all configurations/i })).toBeInTheDocument(),
    );

    await user.click(screen.getByRole("button", { name: /save all configurations/i }));

    // Wait up to 2s for the 1500ms redirect timer
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/main-dashboard"), {
      timeout: 2000,
    });
  });

  it("does not save services that have no URL", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /save all configurations/i })).toBeInTheDocument(),
    );

    // Click save without filling any URL — wait for the success banner to confirm
    // the save flow completed, then verify no individual service was saved
    await user.click(screen.getByRole("button", { name: /save all configurations/i }));

    await waitFor(() =>
      expect(screen.getByText(/configuration saved successfully/i)).toBeInTheDocument(),
    );

    expect(mockSaveServiceConfiguration).not.toHaveBeenCalled();
  });
});
