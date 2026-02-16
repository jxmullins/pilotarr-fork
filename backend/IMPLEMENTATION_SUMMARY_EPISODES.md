# Implementation Summary: TV Show Seasons & Episodes Tracking

## Overview

Successfully implemented comprehensive seasons and episodes tracking for TV shows in Pilotarr backend, synced from Sonarr with monitoring and download status.

**Date**: 2026-02-16
**Status**: ✅ Complete (Backend Only)

---

## What Was Implemented

### 1. Database Models (`app/models/models.py`)

#### Season Model
- **Table**: `seasons`
- **Key Fields**:
  - `library_item_id`: Foreign key to library_items
  - `sonarr_series_id`: Sonarr series ID
  - `season_number`: Season number (indexed)
  - `monitored`: Monitoring status from Sonarr
  - `episode_count`, `episode_file_count`, `total_episode_count`: Episode statistics
  - `size_on_disk`: Size in bytes
  - `statistics`: Full Sonarr statistics (JSON)
- **Relationships**: Belongs to LibraryItem, has many Episodes
- **Indexes**:
  - Unique constraint on (library_item_id, season_number)
  - Index on (sonarr_series_id, season_number)

#### Episode Model
- **Table**: `episodes`
- **Key Fields**:
  - `season_id`: Foreign key to seasons
  - `library_item_id`: Denormalized for fast queries
  - `sonarr_episode_id`: Unique Sonarr episode ID
  - `season_number`, `episode_number`: Episode identifiers
  - `title`, `overview`: Episode metadata
  - `air_date`: Air date (indexed)
  - `monitored`, `has_file`, `downloaded`: Status flags
  - `file_size`, `quality_profile`, `relative_path`: File details
  - `episode_file_info`: Full episode file object (JSON)
- **Relationships**: Belongs to Season and LibraryItem
- **Indexes**:
  - Unique constraint on (sonarr_series_id, season_number, episode_number)
  - Index on (air_date, monitored)
  - Index on (sonarr_series_id, season_number)

### 2. Sonarr API Integration (`app/services/sonarr_connector.py`)

**New Methods**:
- `get_series_by_id(series_id)`: Get single series with full season details
- `get_episodes_by_series(series_id)`: Get all episodes for a series
- `get_episode_files_by_series(series_id)`: Get all episode files with quality/size/path

### 3. Sync Logic (`app/schedulers/sync_service.py`)

#### `sync_sonarr_seasons()`
- **Purpose**: Sync seasons from embedded series data
- **Runs**: Automatically as part of `sync_sonarr()`
- **Process**:
  1. Fetch all TV shows from database
  2. Get series list from Sonarr (includes embedded seasons)
  3. Match by title + year
  4. Upsert seasons with statistics

#### `sync_sonarr_episodes(full_sync=False, series_limit=5)`
- **Purpose**: Sync episodes for TV shows (separate job)
- **Runs**: Manually triggered or via scheduler (less frequent than main sync)
- **Process**:
  1. Get series to sync (monitored only by default, limited batch)
  2. Fetch episodes + episode files from Sonarr
  3. Create file map for fast lookups
  4. Upsert episodes with full metadata and file info
- **Parameters**:
  - `full_sync`: If True, sync all series; if False, only monitored
  - `series_limit`: Max series per run (default: 5, for rate limiting)

### 4. API Endpoints

#### Library Endpoints (`app/api/routes/library.py`)

**GET `/library/{id}/seasons`**
- **Description**: Get all seasons for a TV series
- **Response**: List of SeasonResponse (id, season_number, monitored, episode stats)
- **Validation**: Returns 404 if not a TV series

**GET `/library/{id}/seasons/{season_number}/episodes`**
- **Description**: Get all episodes for a specific season
- **Response**: List of EpisodeResponse (episode details, status, file info)
- **Validation**: Returns 404 if season not found

#### Sync Endpoints (`app/api/routes/sync.py`)

**POST `/sync/trigger/sonarr-episodes`**
- **Description**: Manually trigger episodes sync
- **Query Params**:
  - `full_sync`: bool (default: false)
  - `series_limit`: int (default: 5)
- **Response**: Background task started

### 5. API Schemas (`app/api/schemas.py`)

**SeasonResponse**
- id, season_number, monitored
- episode_count, episode_file_count
- size_on_disk

**EpisodeResponse**
- id, season_number, episode_number
- title, overview, air_date
- monitored, has_file, downloaded
- file_size, quality_profile

### 6. Database Migration (`app/db_migrations_episodes.py`)

- **Purpose**: Create seasons and episodes tables
- **Usage**: `python app/db_migrations_episodes.py` (with proper PYTHONPATH)
- **Safe**: Uses `checkfirst=True` to avoid recreating existing tables

---

## How to Use

### Step 1: Run Migration

```bash
cd /Users/remyjardinet/Documents/Sites/pilotarr/backend
PYTHONPATH=/Users/remyjardinet/Documents/Sites/pilotarr/backend python app/db_migrations_episodes.py
```

**Expected Output**:
```
✅ Tables créées : seasons, episodes
```

### Step 2: Sync Seasons (Automatic)

Seasons are automatically synced when you run the Sonarr sync:

```bash
# Via API
POST /sync/trigger/sonarr

# Or manually
# Seasons sync happens inside sync_sonarr()
```

**What Happens**:
1. Sonarr series are fetched (with embedded seasons)
2. Seasons are upserted with statistics
3. Console output shows: "✅ Sonarr: X séries, Y événements, Z saisons"

### Step 3: Sync Episodes (Manual or Scheduled)

Episodes sync is a separate job for performance reasons.

**Manual Trigger**:
```bash
# Sync 5 monitored series (default)
POST /sync/trigger/sonarr-episodes

# Full sync of 10 series
POST /sync/trigger/sonarr-episodes?full_sync=true&series_limit=10
```

**Expected Output** (in logs):
```
✅ Épisodes: 50 créés, 20 mis à jour (5 séries, 2500ms)
```

### Step 4: Query Data

**Get Seasons for a TV Series**:
```bash
GET /library/{library_item_id}/seasons
```

**Response**:
```json
[
  {
    "id": "uuid",
    "season_number": 1,
    "monitored": true,
    "episode_count": 10,
    "episode_file_count": 8,
    "size_on_disk": 15000000000
  },
  ...
]
```

**Get Episodes for a Season**:
```bash
GET /library/{library_item_id}/seasons/1/episodes
```

**Response**:
```json
[
  {
    "id": "uuid",
    "season_number": 1,
    "episode_number": 1,
    "title": "Pilot",
    "overview": "The first episode...",
    "air_date": "2020-01-15",
    "monitored": true,
    "has_file": true,
    "downloaded": true,
    "file_size": 1500000000,
    "quality_profile": "1080p"
  },
  ...
]
```

---

## Design Decisions

### 1. Two-Phase Sync Approach

**Decision**: Separate sync jobs for seasons and episodes

**Rationale**:
- Seasons change rarely (only when new seasons air)
- Episodes update frequently (downloads, monitoring changes)
- Better error isolation
- Easier rate limiting

**Trade-off**: Slight sync lag, more scheduler complexity

### 2. Denormalized Fields

**Decision**: Store `library_item_id` and `season_number` in Episode

**Rationale**:
- Faster queries without JOINs
- Better index selectivity
- Common query pattern: "Get episodes for series X in season Y"

**Trade-off**: 8 bytes per episode, data consistency risk (mitigated by foreign keys)

### 3. Batch Processing

**Decision**: Process series in batches (default: 5 series per sync)

**Rationale**:
- Rate limiting for Sonarr API
- Better error handling (one series failure doesn't affect others)
- Configurable via `series_limit` parameter

**Trade-off**: Slower full sync, but acceptable for typical usage

### 4. Full JSON Storage

**Decision**: Store full `episode_file_info` and `statistics` as JSON

**Rationale**:
- Preserve all Sonarr data for future use
- Avoid repeated API calls
- Flexible schema (Sonarr may add fields)

**Trade-off**: Larger DB size (acceptable for typical libraries)

---

## Performance Optimizations

### Indexes Created

1. **Season Indexes**:
   - `(library_item_id, season_number)` - UNIQUE, fast season lookups
   - `(sonarr_series_id, season_number)` - Sync optimization

2. **Episode Indexes**:
   - `(sonarr_series_id, season_number, episode_number)` - UNIQUE, fast episode lookups
   - `(air_date, monitored)` - Calendar queries
   - `(sonarr_series_id, season_number)` - Season-level queries

### Query Patterns Optimized

- Get seasons for series: O(log n) lookup via index
- Get episodes for season: O(log n) lookup via index
- Sync episodes: Batch inserts, file map for O(1) lookups

---

## Testing & Verification

### 1. Verify Models Imported

```bash
PYTHONPATH=/Users/remyjardinet/Documents/Sites/pilotarr/backend python -c "from app.models import Season, Episode; print('✅ Models OK')"
```

**Expected**: ✅ Models OK

### 2. Verify Schemas Imported

```bash
PYTHONPATH=/Users/remyjardinet/Documents/Sites/pilotarr/backend python -c "from app.api.schemas import SeasonResponse, EpisodeResponse; print('✅ Schemas OK')"
```

**Expected**: ✅ Schemas OK

### 3. Verify Routes Registered

```bash
PYTHONPATH=/Users/remyjardinet/Documents/Sites/pilotarr/backend python -c "from app.api.routes.library import router; print([r.path for r in router.routes])"
```

**Expected**: `['/library/', '/library/{id}', '/library/{id}/seasons', '/library/{id}/seasons/{season_number}/episodes']`

### 4. Verify Sync Methods Exist

```bash
PYTHONPATH=/Users/remyjardinet/Documents/Sites/pilotarr/backend python -c "from app.schedulers.sync_service import SyncService; print([m for m in dir(SyncService) if 'episode' in m.lower() or 'season' in m.lower()])"
```

**Expected**: `['sync_sonarr_episodes', 'sync_sonarr_seasons']`

---

## Next Steps (Frontend Integration)

1. **Library Page**:
   - Add "Seasons" tab for TV shows
   - Display season cards with episode counts
   - Show monitored/downloaded status

2. **Season Detail Page**:
   - List all episodes with metadata
   - Show download status per episode
   - Display air dates

3. **Manual Sync Trigger**:
   - Add button to trigger episodes sync
   - Show sync progress/status
   - Display last sync time

---

## Files Modified

### New Files
- `backend/app/db_migrations_episodes.py`
- `backend/IMPLEMENTATION_SUMMARY_EPISODES.md` (this file)

### Modified Files
- `backend/app/models/models.py` - Added Season and Episode models
- `backend/app/models/__init__.py` - Exported new models
- `backend/app/services/sonarr_connector.py` - Added episode API methods
- `backend/app/schedulers/sync_service.py` - Added sync logic
- `backend/app/api/schemas.py` - Added response schemas
- `backend/app/api/routes/library.py` - Added endpoints
- `backend/app/api/routes/sync.py` - Added episodes sync trigger

---

## API Reference

### Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/library/{id}/seasons` | Get all seasons for a TV series | - |
| GET | `/library/{id}/seasons/{season_number}/episodes` | Get episodes for a season | - |
| POST | `/sync/trigger/sonarr-episodes` | Trigger episodes sync | - |

### Query Parameters

**POST `/sync/trigger/sonarr-episodes`**:
- `full_sync`: boolean (default: false) - Sync all series or only monitored
- `series_limit`: integer (default: 5) - Max series to process per run

---

## Troubleshooting

### Episodes Not Syncing

**Problem**: Episodes count is 0 after sync

**Solutions**:
1. Check if seasons exist: `SELECT * FROM seasons WHERE library_item_id = 'xxx'`
2. Verify Sonarr connection: Test in Pilotarr settings
3. Check sync logs for errors
4. Manually trigger: `POST /sync/trigger/sonarr-episodes?full_sync=true`

### Slow Episode Sync

**Problem**: Episode sync takes too long

**Solutions**:
1. Reduce `series_limit`: `?series_limit=2`
2. Run sync during off-peak hours
3. Sync only monitored series: `?full_sync=false`

### Missing Episodes

**Problem**: Some episodes missing from database

**Solutions**:
1. Run full sync: `?full_sync=true`
2. Check Sonarr has the episodes
3. Verify series is in library_items
4. Check foreign key constraints

---

## Database Schema

### seasons

```sql
CREATE TABLE seasons (
    id VARCHAR(36) PRIMARY KEY,
    library_item_id VARCHAR(36) NOT NULL,
    sonarr_series_id INTEGER NOT NULL,
    season_number INTEGER NOT NULL,
    monitored BOOLEAN DEFAULT TRUE,
    episode_count INTEGER DEFAULT 0,
    episode_file_count INTEGER DEFAULT 0,
    total_episode_count INTEGER DEFAULT 0,
    size_on_disk BIGINT DEFAULT 0,
    statistics JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (library_item_id) REFERENCES library_items(id) ON DELETE CASCADE,
    UNIQUE KEY (library_item_id, season_number),
    INDEX (sonarr_series_id, season_number)
);
```

### episodes

```sql
CREATE TABLE episodes (
    id VARCHAR(36) PRIMARY KEY,
    season_id VARCHAR(36) NOT NULL,
    library_item_id VARCHAR(36) NOT NULL,
    sonarr_episode_id INTEGER UNIQUE NOT NULL,
    sonarr_series_id INTEGER NOT NULL,
    sonarr_episode_file_id INTEGER,
    season_number INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    absolute_episode_number INTEGER,
    title TEXT,
    overview TEXT,
    air_date DATE,
    air_date_utc DATETIME,
    monitored BOOLEAN DEFAULT TRUE,
    has_file BOOLEAN DEFAULT FALSE,
    downloaded BOOLEAN DEFAULT FALSE,
    file_size BIGINT,
    quality_profile VARCHAR(100),
    relative_path TEXT,
    episode_file_info JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
    FOREIGN KEY (library_item_id) REFERENCES library_items(id) ON DELETE CASCADE,
    UNIQUE KEY (sonarr_series_id, season_number, episode_number),
    INDEX (air_date, monitored),
    INDEX (sonarr_series_id, season_number)
);
```

---

## Credits

**Implementation**: Claude Sonnet 4.5
**Date**: 2026-02-16
**Project**: Pilotarr - TV Show Episodes Tracking
