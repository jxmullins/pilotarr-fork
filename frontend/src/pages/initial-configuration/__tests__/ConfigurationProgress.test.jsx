import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("../../../components/AppIcon", () => ({
  default: ({ name }) => <span data-testid={`icon-${name}`} />,
}));

import ConfigurationProgress from "../components/ConfigurationProgress";

const services = [
  { id: "radarr", name: "Radarr" },
  { id: "sonarr", name: "Sonarr" },
  { id: "jellyfin", name: "Jellyfin" },
  { id: "jellyseerr", name: "Jellyseerr" },
];

const emptyConfigs = services.reduce(
  (acc, s) => ({ ...acc, [s.id]: { url: "", apiKey: "", hasApiKey: false } }),
  {},
);

const fullConfigs = services.reduce(
  (acc, s) => ({ ...acc, [s.id]: { url: "http://localhost", apiKey: "key", hasApiKey: false } }),
  {},
);

const render$ = (testStatuses = {}, configurations = emptyConfigs) =>
  render(
    <ConfigurationProgress
      services={services}
      testStatuses={testStatuses}
      configurations={configurations}
    />,
  );

// ---------------------------------------------------------------------------
// Progress counter
// ---------------------------------------------------------------------------

describe("ConfigurationProgress – progress display", () => {
  it("shows 0 of N connected when nothing is configured", () => {
    render$();
    expect(screen.getByText(`0 of ${services.length} services connected`)).toBeInTheDocument();
  });

  it("shows 0% when no services are alive", () => {
    render$();
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("shows correct count when some services are connected", () => {
    const statuses = { radarr: { status: "success" }, sonarr: { status: "success" } };
    render$(statuses, fullConfigs);
    expect(screen.getByText("2 of 4 services connected")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("shows 100% when all services are connected", () => {
    const statuses = services.reduce((acc, s) => ({ ...acc, [s.id]: { status: "success" } }), {});
    render$(statuses, fullConfigs);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Service state labels
// ---------------------------------------------------------------------------

describe("ConfigurationProgress – service state labels", () => {
  it("shows 'Not configured' for services with no URL", () => {
    render$();
    const labels = screen.getAllByText("Not configured");
    expect(labels).toHaveLength(services.length);
  });

  it("shows 'Configured (not tested)' for services with config but no test", () => {
    const configs = {
      ...emptyConfigs,
      radarr: { url: "http://localhost", apiKey: "key", hasApiKey: false },
    };
    render$({}, configs);
    expect(screen.getByText("Configured (not tested)")).toBeInTheDocument();
  });

  it("shows 'Connected' for services with successful test", () => {
    const statuses = { radarr: { status: "success" } };
    render$(statuses, fullConfigs);
    expect(screen.getByText("Connected")).toBeInTheDocument();
  });

  it("shows 'Test failed' for services with error test", () => {
    const statuses = { radarr: { status: "error" } };
    render$(statuses, fullConfigs);
    expect(screen.getByText("Test failed")).toBeInTheDocument();
  });

  it("shows 'Testing...' for services currently being tested", () => {
    const statuses = { radarr: { status: "testing" } };
    render$(statuses, fullConfigs);
    expect(screen.getByText("Testing...")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Summary warnings
// ---------------------------------------------------------------------------

describe("ConfigurationProgress – summary warnings", () => {
  it("shows configured-but-not-tested warning when applicable", () => {
    const configs = {
      ...emptyConfigs,
      radarr: { url: "http://localhost", apiKey: "key", hasApiKey: false },
    };
    render$({}, configs);
    // The label appears both in the summary bar and the service tile
    expect(screen.getAllByText(/configured \(not tested\)/i).length).toBeGreaterThan(0);
  });

  it("shows test failed warning when applicable", () => {
    const statuses = { radarr: { status: "error" } };
    render$(statuses, fullConfigs);
    expect(screen.getAllByText(/test failed/i).length).toBeGreaterThan(0);
  });

  it("shows all-connected success banner when 100% connected", () => {
    const statuses = services.reduce((acc, s) => ({ ...acc, [s.id]: { status: "success" } }), {});
    render$(statuses, fullConfigs);
    expect(
      screen.getByText(/all services configured and connected successfully/i),
    ).toBeInTheDocument();
  });

  it("does not show all-connected banner when not all services are connected", () => {
    const statuses = { radarr: { status: "success" } };
    render$(statuses, fullConfigs);
    expect(
      screen.queryByText(/all services configured and connected successfully/i),
    ).not.toBeInTheDocument();
  });
});
