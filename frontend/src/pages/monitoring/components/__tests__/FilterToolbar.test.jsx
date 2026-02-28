import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("../../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

// Minimal Select stub that renders a native <select>
vi.mock("../../../../components/ui/Select", () => ({
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

vi.mock("../../../../components/ui/Button", () => ({
  default: ({ children, onClick }) => <button onClick={onClick}>{children}</button>,
}));

import FilterToolbar from "../FilterToolbar";

const defaultProps = {
  searchQuery: "",
  onSearchChange: vi.fn(),
  filters: { service: "all", status: "all", quality: "all" },
  onFilterChange: vi.fn(),
  totalResults: 10,
};

const render$ = (props = {}) => render(<FilterToolbar {...defaultProps} {...props} />);

describe("FilterToolbar – rendering", () => {
  it("renders the search input", () => {
    render$();
    expect(screen.getByPlaceholderText(/search media by title/i)).toBeInTheDocument();
  });

  it("shows total results count", () => {
    render$({ totalResults: 42 });
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("does not show Clear Filters button when nothing is active", () => {
    render$();
    expect(screen.queryByText(/clear filters/i)).not.toBeInTheDocument();
  });

  it("shows Clear Filters button when a filter is active", () => {
    render$({ filters: { service: "sonarr", status: "all", quality: "all" } });
    expect(screen.getByText(/clear filters/i)).toBeInTheDocument();
  });

  it("shows Clear Filters button when search is active", () => {
    render$({ searchQuery: "Breaking Bad" });
    expect(screen.getByText(/clear filters/i)).toBeInTheDocument();
  });
});

describe("FilterToolbar – interactions", () => {
  it("calls onSearchChange when typing in the search box", async () => {
    const user = userEvent.setup();
    const onSearchChange = vi.fn();
    render$({ onSearchChange });

    await user.type(screen.getByPlaceholderText(/search media by title/i), "Oz");

    expect(onSearchChange).toHaveBeenCalled();
  });

  it("calls onFilterChange with correct args when service changes", async () => {
    const user = userEvent.setup();
    const onFilterChange = vi.fn();
    render$({ onFilterChange });

    await user.selectOptions(screen.getByTestId("select-Service"), "sonarr");

    expect(onFilterChange).toHaveBeenCalledWith("service", "sonarr");
  });

  it("calls onFilterChange with correct args when status changes to monitored", async () => {
    const user = userEvent.setup();
    const onFilterChange = vi.fn();
    render$({ onFilterChange });

    await user.selectOptions(screen.getByTestId("select-Status"), "monitored");

    expect(onFilterChange).toHaveBeenCalledWith("status", "monitored");
  });

  it("calls onFilterChange with correct args when status changes to unmonitored", async () => {
    const user = userEvent.setup();
    const onFilterChange = vi.fn();
    render$({ onFilterChange });

    await user.selectOptions(screen.getByTestId("select-Status"), "unmonitored");

    expect(onFilterChange).toHaveBeenCalledWith("status", "unmonitored");
  });

  it("clears all filters when Clear Filters is clicked", async () => {
    const user = userEvent.setup();
    const onSearchChange = vi.fn();
    const onFilterChange = vi.fn();
    render$({
      searchQuery: "test",
      onSearchChange,
      onFilterChange,
      filters: { service: "sonarr", status: "monitored", quality: "all" },
    });

    await user.click(screen.getByText(/clear filters/i));

    expect(onSearchChange).toHaveBeenCalledWith("");
    expect(onFilterChange).toHaveBeenCalledWith("service", "all");
    expect(onFilterChange).toHaveBeenCalledWith("status", "all");
    expect(onFilterChange).toHaveBeenCalledWith("quality", "all");
  });
});
