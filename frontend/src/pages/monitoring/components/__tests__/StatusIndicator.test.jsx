import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("../../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

import StatusIndicator from "../StatusIndicator";

describe("StatusIndicator – monitoring type", () => {
  it("renders Monitored label for monitored status", () => {
    render(<StatusIndicator status="monitored" type="monitoring" />);
    expect(screen.getByText("Monitored")).toBeInTheDocument();
    expect(screen.getByTestId("icon-Eye")).toBeInTheDocument();
  });

  it("renders Unmonitored label for unmonitored status", () => {
    render(<StatusIndicator status="unmonitored" type="monitoring" />);
    expect(screen.getByText("Unmonitored")).toBeInTheDocument();
    expect(screen.getByTestId("icon-EyeOff")).toBeInTheDocument();
  });

  it("renders Unknown for unrecognised monitoring status", () => {
    render(<StatusIndicator status="something-else" type="monitoring" />);
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });
});

describe("StatusIndicator – availability type", () => {
  it("renders Available label", () => {
    render(<StatusIndicator status="available" type="availability" />);
    expect(screen.getByText("Available")).toBeInTheDocument();
    expect(screen.getByTestId("icon-CheckCircle2")).toBeInTheDocument();
  });

  it("renders Missing label", () => {
    render(<StatusIndicator status="missing" type="availability" />);
    expect(screen.getByText("Missing")).toBeInTheDocument();
    expect(screen.getByTestId("icon-AlertCircle")).toBeInTheDocument();
  });

  it("renders Downloading label", () => {
    render(<StatusIndicator status="downloading" type="availability" />);
    expect(screen.getByText("Downloading")).toBeInTheDocument();
    expect(screen.getByTestId("icon-Download")).toBeInTheDocument();
  });

  it("renders Unknown for unrecognised availability status", () => {
    render(<StatusIndicator status="weird" type="availability" />);
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });
});

describe("StatusIndicator – unknown type", () => {
  it("renders Unknown when type is unrecognised", () => {
    render(<StatusIndicator status="monitored" type="other" />);
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });
});
