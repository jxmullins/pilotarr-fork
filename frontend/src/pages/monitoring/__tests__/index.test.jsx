import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

// --- Mocks ---

vi.mock("../../../components/navigation/Header", () => ({
  default: () => <header data-testid="header" />,
}));

vi.mock("../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

vi.mock("../../../components/ui/Button", () => ({
  default: ({ children, onClick }) => <button onClick={onClick}>{children}</button>,
}));

// Minimal Select stub
vi.mock("../../../components/ui/Select", () => ({
  default: ({ options, value, onChange, placeholder }) => (
    <select
      aria-label={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      data-testid={`select-${placeholder}`}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  ),
}));

vi.mock("../../../components/ui/Checkbox", () => ({
  Checkbox: ({ checked, onChange }) => (
    <input type="checkbox" checked={checked} onChange={onChange} />
  ),
}));

vi.mock("../components/StatusIndicator", () => ({
  default: ({ status, type }) => <span data-testid={`status-${type}-${status}`}>{status}</span>,
}));

vi.mock("../components/ExpandableRow", () => ({
  default: ({ item }) => <div data-testid={`expanded-${item.id}`}>{item.title}</div>,
}));

const mockGetMonitoringItems = vi.fn();
vi.mock("../../../services/monitoringService", () => ({
  getMonitoringItems: (...args) => mockGetMonitoringItems(...args),
}));

import Monitoring from "../index";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const makeItem = (overrides = {}) => ({
  id: "1",
  title: "Inception",
  year: 2010,
  service: "radarr",
  monitoring_status: "monitored",
  availability_status: "available",
  quality_profile: "1080p",
  last_updated: "2024-01-15T10:00:00Z",
  file_size: "12 GB",
  image_url: null,
  seasons: [],
  download_history: [],
  ...overrides,
});

const renderPage = () =>
  render(
    <MemoryRouter>
      <Monitoring />
    </MemoryRouter>,
  );

beforeEach(() => {
  vi.clearAllMocks();
  mockGetMonitoringItems.mockResolvedValue([]);
});

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe("Monitoring page – rendering", () => {
  it("shows loading spinner while fetching", () => {
    mockGetMonitoringItems.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading monitoring data/i)).toBeInTheDocument();
  });

  it("renders the page heading after loading", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /media monitoring/i })).toBeInTheDocument(),
    );
  });

  it("renders the filter toolbar after loading", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByPlaceholderText(/search media by title/i)).toBeInTheDocument(),
    );
  });

  it("shows error banner when fetch fails", async () => {
    mockGetMonitoringItems.mockRejectedValue(new Error("Network error"));
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/failed to load monitoring data/i)).toBeInTheDocument(),
    );
  });

  it("renders item titles from API data", async () => {
    mockGetMonitoringItems.mockResolvedValue([makeItem()]);
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Inception").length).toBeGreaterThan(0));
  });
});

// ---------------------------------------------------------------------------
// Status filter — the bug this test suite was written to prevent
// ---------------------------------------------------------------------------

describe("Monitoring page – status filter (regression)", () => {
  const items = [
    makeItem({
      id: "1",
      title: "Movie A",
      monitoring_status: "monitored",
      availability_status: "available",
    }),
    makeItem({
      id: "2",
      title: "Movie B",
      monitoring_status: "unmonitored",
      availability_status: "missing",
    }),
    makeItem({
      id: "3",
      title: "Movie C",
      monitoring_status: "monitored",
      availability_status: "missing",
    }),
  ];

  beforeEach(() => {
    mockGetMonitoringItems.mockResolvedValue(items);
  });

  it("shows all items when status filter is 'all'", async () => {
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Movie A").length).toBeGreaterThan(0));
    expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Movie C").length).toBeGreaterThan(0);
  });

  it("filters by 'monitored' — shows only monitored items", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Movie A").length).toBeGreaterThan(0));

    await user.selectOptions(screen.getByTestId("select-Status"), "monitored");

    await waitFor(() => {
      expect(screen.getAllByText("Movie A").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Movie C").length).toBeGreaterThan(0);
      expect(screen.queryByText("Movie B")).not.toBeInTheDocument();
    });
  });

  it("filters by 'unmonitored' — shows only unmonitored items", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0));

    await user.selectOptions(screen.getByTestId("select-Status"), "unmonitored");

    await waitFor(() => {
      expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0);
      expect(screen.queryByText("Movie A")).not.toBeInTheDocument();
      expect(screen.queryByText("Movie C")).not.toBeInTheDocument();
    });
  });

  it("filters by 'available' — uses availabilityStatus, not monitoringStatus", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Movie A").length).toBeGreaterThan(0));

    await user.selectOptions(screen.getByTestId("select-Status"), "available");

    await waitFor(() => {
      expect(screen.getAllByText("Movie A").length).toBeGreaterThan(0);
      expect(screen.queryByText("Movie B")).not.toBeInTheDocument();
      expect(screen.queryByText("Movie C")).not.toBeInTheDocument();
    });
  });

  it("filters by 'missing' — uses availabilityStatus", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0));

    await user.selectOptions(screen.getByTestId("select-Status"), "missing");

    await waitFor(() => {
      expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Movie C").length).toBeGreaterThan(0);
      expect(screen.queryByText("Movie A")).not.toBeInTheDocument();
    });
  });
});

// ---------------------------------------------------------------------------
// Service filter
// ---------------------------------------------------------------------------

describe("Monitoring page – service filter", () => {
  const items = [
    makeItem({ id: "1", title: "Show A", service: "sonarr" }),
    makeItem({ id: "2", title: "Movie B", service: "radarr" }),
  ];

  beforeEach(() => {
    mockGetMonitoringItems.mockResolvedValue(items);
  });

  it("filters by sonarr", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Show A").length).toBeGreaterThan(0));

    await user.selectOptions(screen.getByTestId("select-Service"), "sonarr");

    await waitFor(() => {
      expect(screen.getAllByText("Show A").length).toBeGreaterThan(0);
      expect(screen.queryByText("Movie B")).not.toBeInTheDocument();
    });
  });

  it("filters by radarr", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0));

    await user.selectOptions(screen.getByTestId("select-Service"), "radarr");

    await waitFor(() => {
      expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0);
      expect(screen.queryByText("Show A")).not.toBeInTheDocument();
    });
  });
});

// ---------------------------------------------------------------------------
// Search filter
// ---------------------------------------------------------------------------

describe("Monitoring page – search filter", () => {
  beforeEach(() => {
    mockGetMonitoringItems.mockResolvedValue([
      makeItem({ id: "1", title: "Inception" }),
      makeItem({ id: "2", title: "The Matrix" }),
    ]);
  });

  it("filters items by search query", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Inception").length).toBeGreaterThan(0));

    await user.type(screen.getByPlaceholderText(/search media by title/i), "matrix");

    await waitFor(() => {
      expect(screen.getAllByText("The Matrix").length).toBeGreaterThan(0);
      expect(screen.queryByText("Inception")).not.toBeInTheDocument();
    });
  });

  it("search is case-insensitive", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getAllByText("Inception").length).toBeGreaterThan(0));

    await user.type(screen.getByPlaceholderText(/search media by title/i), "INCEPTION");

    await waitFor(() => expect(screen.getAllByText("Inception").length).toBeGreaterThan(0));
  });
});

// ---------------------------------------------------------------------------
// Result count
// ---------------------------------------------------------------------------

describe("Monitoring page – result count", () => {
  it("shows correct count after filtering", async () => {
    const user = userEvent.setup();
    mockGetMonitoringItems.mockResolvedValue([
      makeItem({ id: "1", monitoring_status: "monitored" }),
      makeItem({ id: "2", title: "Movie 2", monitoring_status: "unmonitored" }),
    ]);
    renderPage();
    await waitFor(() => expect(screen.getByText("2")).toBeInTheDocument());

    await user.selectOptions(screen.getByTestId("select-Status"), "monitored");

    await waitFor(() => expect(screen.getByText("1")).toBeInTheDocument());
  });
});
