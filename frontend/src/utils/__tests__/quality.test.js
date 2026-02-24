import { describe, it, expect } from "vitest";
import { formatQuality } from "../quality";

describe("formatQuality", () => {
  it("returns null for falsy input", () => {
    expect(formatQuality(null)).toBeNull();
    expect(formatQuality("")).toBeNull();
    expect(formatQuality(undefined)).toBeNull();
  });

  it("returns numeric-only strings as-is (old profile IDs)", () => {
    expect(formatQuality("1080")).toBe("1080");
    expect(formatQuality("720")).toBe("720");
  });

  it("extracts Blu-ray source", () => {
    expect(formatQuality("Bluray-1080p")).toBe("Blu-ray 1080p");
    expect(formatQuality("BDRip-720p")).toBe("Blu-ray 720p");
  });

  it("extracts WEB source from WEBRip", () => {
    expect(formatQuality("WEBRip-1080p")).toBe("WEB 1080p");
  });

  it("extracts WEB source from WEBDL (web key matches before web-dl)", () => {
    // SOURCE_MAP iterates 'web' before 'web-dl', so WEB-DL matches as "WEB"
    expect(formatQuality("WEBDL-1080p")).toBe("WEB 1080p");
  });

  it("extracts HDTV source", () => {
    expect(formatQuality("HDTV-720p")).toBe("HDTV 720p");
  });

  it("maps 2160p to 4K", () => {
    expect(formatQuality("Bluray-2160p")).toBe("Blu-ray 4K");
  });

  it("maps 480p resolution", () => {
    expect(formatQuality("HDTV-480p")).toBe("HDTV 480p");
  });

  it("detects HDR flag", () => {
    const result = formatQuality("Bluray-2160p-HDR");
    expect(result).toContain("HDR");
    expect(result).toContain("Blu-ray");
    expect(result).toContain("4K");
  });

  it("returns original string when nothing matches", () => {
    expect(formatQuality("Unknown Profile")).toBe("Unknown Profile");
  });

  it("is case-insensitive", () => {
    expect(formatQuality("WEBRIP-1080P")).toBe("WEB 1080p");
    expect(formatQuality("bluray-720p")).toBe("Blu-ray 720p");
  });
});
