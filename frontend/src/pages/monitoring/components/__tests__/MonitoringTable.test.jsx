import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("../../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

vi.mock("../../../../components/ui/Button", () => ({
  default: ({ children, onClick }) => <button onClick={onClick}>{children || ""}</button>,
}));

vi.mock("../../../../components/ui/Checkbox", () => ({
  Checkbox: ({ checked, onChange }) => (
    <input type="checkbox" checked={checked} onChange={onChange} />
  ),
}));

vi.mock("../StatusIndicator", () => ({
  default: ({ status, type }) => <span data-testid={`status-${type}-${status}`}>{status}</span>,
}));

vi.mock("../ExpandableRow", () => ({
  default: ({ item }) => <div data-testid={`expanded-${item.id}`}>Expanded: {item.title}</div>,
}));

import MonitoringTable from "../MonitoringTable";

const makeItem = (overrides = {}) => ({
  id: "1",
  title: "Inception",
  service: "radarr",
  monitoringStatus: "monitored",
  availabilityStatus: "available",
  qualityProfile: "1080p",
  lastUpdated: "2024-01-15T10:00:00Z",
  seasons: [],
  downloadHistory: [],
  ...overrides,
});

const defaultProps = {
  data: [],
  selectedItems: [],
  onSelectAll: vi.fn(),
  onSelectItem: vi.fn(),
};

const render$ = (props = {}) => render(<MonitoringTable {...defaultProps} {...props} />);

describe("MonitoringTable – empty state", () => {
  it("shows empty state message when data is empty", () => {
    render$();
    expect(screen.getByText(/no monitored media found/i)).toBeInTheDocument();
  });
});

describe("MonitoringTable – rendering rows", () => {
  it("renders item title", () => {
    render$({ data: [makeItem()] });
    expect(screen.getAllByText("Inception").length).toBeGreaterThan(0);
  });

  it("renders service badge", () => {
    render$({ data: [makeItem()] });
    expect(screen.getAllByText("radarr").length).toBeGreaterThan(0);
  });

  it("renders monitoring and availability status indicators", () => {
    render$({ data: [makeItem()] });
    expect(screen.getAllByTestId("status-monitoring-monitored").length).toBeGreaterThan(0);
    expect(screen.getAllByTestId("status-availability-available").length).toBeGreaterThan(0);
  });

  it("renders quality profile", () => {
    render$({ data: [makeItem()] });
    expect(screen.getAllByText("1080p").length).toBeGreaterThan(0);
  });

  it("renders multiple rows", () => {
    const data = [makeItem({ id: "1", title: "Movie A" }), makeItem({ id: "2", title: "Movie B" })];
    render$({ data });
    expect(screen.getAllByText("Movie A").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Movie B").length).toBeGreaterThan(0);
  });
});

describe("MonitoringTable – expand/collapse row", () => {
  it("does not show expanded content initially", () => {
    render$({ data: [makeItem({ id: "42" })] });
    expect(screen.queryByTestId("expanded-42")).not.toBeInTheDocument();
  });

  it("shows expanded content after clicking the expand button", async () => {
    const user = userEvent.setup();
    render$({ data: [makeItem({ id: "42", title: "Inception" })] });

    // The expand toggle buttons render ChevronRight icons — click the first one
    const expandButtons = screen
      .getAllByRole("button")
      .filter((btn) => btn.querySelector('[data-testid="icon-ChevronRight"]'));
    await user.click(expandButtons[0]);

    expect(screen.getAllByTestId("expanded-42").length).toBeGreaterThan(0);
  });
});

describe("MonitoringTable – sorting", () => {
  it("renders items in default ascending title order", () => {
    const data = [makeItem({ id: "1", title: "Zebra" }), makeItem({ id: "2", title: "Alpha" })];
    render$({ data });
    const titles = screen.getAllByText(/Zebra|Alpha/).map((el) => el.textContent);
    // Alpha should appear before Zebra in sorted order
    expect(titles.indexOf("Alpha")).toBeLessThan(titles.indexOf("Zebra"));
  });

  it("clicking Title header reverses sort direction", async () => {
    const user = userEvent.setup();
    const data = [makeItem({ id: "1", title: "Zebra" }), makeItem({ id: "2", title: "Alpha" })];
    render$({ data });

    await user.click(screen.getByText("Title"));

    // After clicking (desc), Zebra should come before Alpha
    const titles = screen.getAllByText(/Zebra|Alpha/).map((el) => el.textContent);
    expect(titles.indexOf("Zebra")).toBeLessThan(titles.indexOf("Alpha"));
  });
});

describe("MonitoringTable – selection", () => {
  it("calls onSelectItem when a row checkbox is clicked", async () => {
    const user = userEvent.setup();
    const onSelectItem = vi.fn();
    render$({ data: [makeItem({ id: "1" })], onSelectItem });

    const checkboxes = screen.getAllByRole("checkbox");
    // First checkbox is select-all, second is the row checkbox
    await user.click(checkboxes[1]);

    expect(onSelectItem).toHaveBeenCalledWith("1", true);
  });

  it("calls onSelectAll when header checkbox is clicked", async () => {
    const user = userEvent.setup();
    const onSelectAll = vi.fn();
    render$({ data: [makeItem()], onSelectAll });

    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[0]);

    expect(onSelectAll).toHaveBeenCalled();
  });
});
