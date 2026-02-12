<!--
UPDATE WHEN:
- Adding new entry points or key files
- Introducing new patterns
- Discovering non-obvious behavior

Helps quickly navigate the codebase when resuming work.
-->

# Code Landmarks

Quick reference to important parts of the codebase.

## Entry Points
| Location | Purpose |
|----------|---------|
| backend/app/main.py | FastAPI application entry point |
| frontend/src/index.jsx | React app entry point |
| frontend/src/App.jsx | Root React component |
| frontend/src/Routes.jsx | React Router configuration |
| backend/docker-compose.yml | Docker Compose for full stack |

## Core Business Logic
| Location | Purpose |
|----------|---------|
| backend/app/services/ | Service connectors (Radarr, Sonarr, Jellyfin, etc.) |
| backend/app/services/base_connector.py | Base class for all service connectors |
| backend/app/api/routes/ | API route handlers |
| backend/app/models/ | SQLAlchemy database models |
| backend/app/schedulers/ | APScheduler background tasks |

## Configuration
| Location | Purpose |
|----------|---------|
| .env | Environment variables (DB, API keys) |
| backend/app/core/ | App configuration module |
| frontend/vite.config.mjs | Vite build configuration |
| frontend/tailwind.config.js | Tailwind CSS configuration |

## Frontend Structure
| Location | Purpose |
|----------|---------|
| frontend/src/pages/ | Page components (folder per feature) |
| frontend/src/components/ | Shared UI components |
| frontend/src/services/ | API client (Axios) |
| frontend/src/contexts/ | React context providers |
| frontend/src/utils/ | Utility functions |

## Key Patterns
| Pattern | Example Location | Notes |
|---------|------------------|-------|
| Service Connector | backend/app/services/radarr_connector.py | Inherits from base_connector.py |
| API Routes | backend/app/api/routes/ | FastAPI router pattern |
| Page Components | frontend/src/pages/main-dashboard/ | Folder per feature/page |

## Testing
| Location | Purpose |
|----------|---------|
| backend/test_db.py | Database connection test |
| (TODO) backend/tests/ | Backend test suite |
| (TODO) frontend/src/__tests__/ | Frontend test suite |

## Gotchas & Non-Obvious Behavior
| Location | Issue | Notes |
|----------|-------|-------|
| frontend/package.json | rocketCritical section | DO NOT remove marked dependencies |
| .env | Contains real secrets | Never commit, use .env.example |
