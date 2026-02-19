/**
 * Normalize a Radarr/Sonarr quality string to a short, human-readable label.
 *
 * Radarr stores names like "Bluray-1080p", "WEBRip-2160p", "HDTV-720p".
 * Sonarr quality profile names are user-defined but follow the same conventions.
 * This function extracts the resolution and source into a compact badge label.
 */

const SOURCE_MAP = {
  bluray: "Blu-ray",
  "blu-ray": "Blu-ray",
  bdrip: "Blu-ray",
  brrip: "Blu-ray",
  remux: "Remux",
  web: "WEB",
  webrip: "WEB",
  webdl: "WEB-DL",
  "web-dl": "WEB-DL",
  hdtv: "HDTV",
  dvd: "DVD",
  cam: "CAM",
  ts: "TS",
  screener: "SCR",
  raw: "RAW",
};

const RESOLUTION_MAP = {
  2160: "4K",
  1080: "1080p",
  720: "720p",
  576: "576p",
  480: "480p",
  360: "360p",
};

export const formatQuality = (quality) => {
  if (!quality) return null;

  // Already a pure numeric string — still an old profile ID, return as-is
  if (/^\d+$/.test(quality.trim())) return quality;

  const lower = quality.toLowerCase().replace(/[_\s]+/g, "-");

  // Extract resolution (2160, 1080, 720, 576, 480, 360)
  const resMatch = lower.match(/(\d{3,4})p?/);
  const resNum = resMatch ? parseInt(resMatch[1], 10) : null;
  const resLabel = resNum ? RESOLUTION_MAP[resNum] || `${resNum}p` : null;

  // Detect HDR
  const isHDR = /hdr|dolby.?vision|dv\b/.test(lower);

  // Detect source
  let sourceLabel = null;
  for (const [key, label] of Object.entries(SOURCE_MAP)) {
    if (lower.includes(key)) {
      sourceLabel = label;
      break;
    }
  }

  const parts = [];
  if (sourceLabel) parts.push(sourceLabel);
  if (resLabel) parts.push(resLabel);
  if (isHDR) parts.push("HDR");

  return parts.length > 0 ? parts.join(" ") : quality;
};
