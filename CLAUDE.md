# UmbrellaMC System Architecture

## Project Identity & Tech Stack

### Project Overview
**Project Name:** UmbrellaMC — A comprehensive Minecraft server management platform integrating Discord moderation, player analytics, and real-time server monitoring.

### Core Technology Stack

#### Frontend (Dashboard)
- **Runtime:** Node.js 18+
- **Framework:** Next.js 16.2.6 (App Router)
- **Language:** TypeScript 5.7.3
- **UI Library:** React 19
- **Styling:** Tailwind CSS 4.2.0 + shadcn/ui components
- **State Management:** @tanstack/react-query 5.101.0
- **Charts:** Recharts 3.8.0
- **Icons:** Lucide React 1.16.0

#### Backend (Umbrella Core)
- **Runtime:** Python 3.12
- **Framework:** FastAPI 0.115.5
- **Server:** Uvicorn 0.32.1
- **Database:** PostgreSQL 14+ with async support (SQLAlchemy 2.0.36, asyncpg 0.30.0)
- **Cache/Session:** Redis 5.2.1, aioredis 2.0.1
- **Migrations:** Alembic 1.14.0
- **Validation:** Pydantic 2.10.3, pydantic-settings 2.6.1

#### Discord Bot
- **Runtime:** Python 3.12
- **Library:** py-cord 2.4.0+
- **HTTP Client:** httpx 0.27.0+

#### Minecraft Integration
- **Server:** Paper 1.20.4
- **Language:** Java 17
- **Build Tool:** Maven 3.8+
- **Dependencies:** ProtocolLib 5.3.0, OkHttp 4.12.0, Gson 2.10.1

### Build & Execution Commands

```bash
# Dashboard (Next.js)
cd Dashboard
pnpm install          # Install dependencies (uses pnpm)
pnpm dev              # Start development server
pnpm build            # Build for production
pnpm start            # Run production build

# Backend (Umbrella Core)
cd files/umbrella-core
python -m venv .venv && source .venv/bin/activate  # Create virtual environment
pip install -r requirements.txt                     # Install dependencies
python main.py                                      # Run with uvicorn
alembic upgrade head                                # Run migrations

# Discord Bot
cd discord-bot
pip install -r requirements.txt
python main.py

# Minecraft Plugin
cd minecraft-plugin
mvn clean package                                   # Build JAR
```

---

## Exhaustive Directory Mapping

```
Root
├── .git/                              # Git version control
├── .vscode/                           # VSCode settings
├── Dashboard/                         # Next.js 16 web dashboard
│   ├── app/                           # Next.js App Router pages
│   │   ├── ai-config/                 # AI configuration management page
│   │   ├── ai-tasks/                  # AI task management page
│   │   ├── alts/                      # Alternate account detection page
│   │   ├── analytics/                 # Analytics dashboard page
│   │   ├── announcements/             # Announcement management page
│   │   ├── appeals/                   # Player appeal system page
│   │   ├── audit/                     # Audit log viewer page
│   │   ├── login/                     # Authentication login page
│   │   ├── no-access/                 # Access denied page
│   │   ├── players/                   # Player directory with [uuid] dynamic route
│   │   ├── plugins/                   # Plugin management page
│   │   ├── punishments/               # Punishment management page
│   │   ├── replay/                    # Replay viewer with [id] dynamic route
│   │   ├── servers/                   # Server status/management page
│   │   ├── settings/                  # System settings page
│   │   ├── snapshots/                 # Player snapshot viewer with [id] route
│   │   ├── staff/                     # Staff management page
│   │   ├── system/                    # System status page
│   │   ├── translation/               # Translation management page
│   │   ├── verification/              # Player verification page
│   │   ├── layout.tsx                 # Root layout with providers
│   │   ├── page.tsx                   # Landing/home page
│   │   └── globals.css                # Global Tailwind styles
│   ├── components/                    # React components
│   │   ├── dashboard/                 # Dashboard-specific components (charts, stat cards)
│   │   ├── players/                   # Player-related components (tables)
│   │   ├── ui/                        # shadcn/ui base components (30+ components)
│   │   ├── add-staff-dialog.tsx       # Staff addition modal
│   │   ├── app-shell.tsx              # App shell wrapper
│   │   ├── app-sidebar.tsx            # Main sidebar navigation
│   │   ├── auth-context.tsx           # Authentication context provider
│   │   ├── auth-guard.tsx             # Route protection component
│   │   ├── global-search.tsx          # Global search component
│   │   ├── new-punishment-dialog.tsx  # Punishment creation modal
│   │   ├── page-header.tsx            # Page header with title
│   │   ├── player-avatar.tsx          # Player avatar component
│   │   ├── providers.tsx              # React Query + Theme providers
│   │   ├── status-badge.tsx           # Status indicator badge
│   │   └── top-bar.tsx                # Top navigation bar
│   ├── hooks/                         # Custom React hooks
│   │   └── use-mobile.ts              # Mobile viewport detection
│   ├── lib/                           # Utility libraries
│   │   ├── api-config.ts              # API configuration constants
│   │   ├── api.ts                     # Axios/fetch wrapper for API calls
│   │   ├── format.ts                  # Data formatting utilities
│   │   ├── mock-data.ts               # Development mock data
│   │   ├── nav.ts                     # Navigation configuration
│   │   ├── queries.ts                 # React Query hooks
│   │   ├── transforms.ts              # Data transformation utilities
│   │   ├── types.ts                   # TypeScript type definitions
│   │   └── utils.ts                   # General utilities
│   ├── public/                        # Static assets
│   ├── package.json                   # npm dependencies
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── next.config.mjs                # Next.js configuration
│   └── postcss.config.mjs             # PostCSS configuration
│
├── files/                             # Backend and utilities
│   ├── umbrella-core/                 # Main FastAPI backend (Umbrella Core)
│   │   ├── api/                       # FastAPI application
│   │   │   ├── dependencies/          # Dependency injection
│   │   │   │   └── permissions.py     # Permission checker
│   │   │   ├── middleware/            # FastAPI middleware
│   │   │   │   ├── audit.py           # Audit logging middleware
│   │   │   │   ├── auth.py            # Authentication middleware
│   │   │   │   ├── errors.py          # Error handling middleware
│   │   │   │   ├── permissions.py     # Permission middleware
│   │   │   │   └── session.py         # Session management middleware
│   │   │   ├── routers/               # API route handlers (22 routers)
│   │   │   │   ├── ai_config.py       # AI configuration endpoints
│   │   │   │   ├── ai_tasks.py        # AI task endpoints
│   │   │   │   ├── alt_detection.py   # Alt account detection endpoints
│   │   │   │   ├── analytics.py       # Analytics data endpoints
│   │   │   │   ├── anticheat.py       # Anticheat system endpoints
│   │   │   │   ├── appeals.py         # Appeal management endpoints
│   │   │   │   ├── audit.py           # Audit log endpoints
│   │   │   │   ├── auth.py            # Authentication endpoints
│   │   │   │   ├── bridge.py          # Discord-MC bridge endpoints
│   │   │   │   ├── dashboard.py       # Dashboard meta endpoints
│   │   │   │   ├── health.py          # Health check endpoint
│   │   │   │   ├── mc_commands.py     # MC command endpoints
│   │   │   │   ├── moderation.py      # Moderation endpoints
│   │   │   │   ├── players.py         # Player data endpoints
│   │   │   │   ├── plugin.py          # Plugin management endpoints
│   │   │   │   ├── punishments.py     # Punishment endpoints
│   │   │   │   ├── replay.py          # Replay system endpoints
│   │   │   │   ├── roles.py           # Role management endpoints
│   │   │   │   ├── server_control.py  # Server control endpoints
│   │   │   │   ├── settings.py        # Settings endpoints
│   │   │   │   ├── snapshot.py        # Player snapshot endpoints
│   │   │   │   ├── staff.py           # Staff management endpoints
│   │   │   │   ├── translation.py     # Translation endpoints
│   │   │   │   └── verification.py    # Player verification endpoints
│   │   │   └── schemas/               # Pydantic request/response schemas
│   │   ├── config/                    # Configuration management
│   │   │   └── settings.py            # Settings class with .env loading
│   │   ├── database/                  # Database connection
│   │   │   ├── __init__.py            # Database initialization
│   │   │   └── engine.py              # SQLAlchemy async engine setup
│   │   ├── models/                    # SQLAlchemy ORM models (18 models)
│   │   │   ├── ai_config.py           # AI configuration model
│   │   │   │   ├── ai_tasks.py        # AI task model
│   │   │   │   ├── alt_detection.py   # Alt account detection model
│   │   │   │   ├── analytics.py       # Analytics data model
│   │   │   │   ├── audit_log.py       # Audit log model
│   │   │   │   ├── discord.py         # Discord integration model
│   │   │   │   ├── mc_commands.py     # Minecraft command model
│   │   │   │   ├── permissions.py     # Permissions model
│   │   │   │   ├── player.py          # Player profile model
│   │   │   │   ├── plugin_command.py  # Plugin command model
│   │   │   │   ├── plugin_heartbeat.py# Plugin heartbeat model
│   │   │   │   ├── replay.py          # Replay data model
│   │   │   │   ├── setting.py         # System settings model
│   │   │   │   ├── snapshot.py        # Player snapshot model
│   │   │   │   ├── translation.py     # Translation model
│   │   │   │   ├── user.py            # User/auth model
│   │   │   │   └── verification.py    # Player verification model
│   │   ├── services/                  # Business logic services (14 services)
│   │   │   ├── ai_config_service.py   # AI config CRUD operations
│   │   │   │   ├── ai_service.py      # AI task execution service
│   │   │   │   ├── alt_detection_service.py  # Alt detection logic
│   │   │   │   ├── analytics_service.py      # Analytics aggregation
│   │   │   │   ├── anticheat_service.py      # Anticheat integration
│   │   │   │   ├── discord_service.py        # Discord API integration
│   │   │   │   ├── replay_service.py         # Replay management
│   │   │   │   ├── roles_service.py          # Role management
│   │   │   │   ├── server_control_service.py # Server control (RCON)
│   │   │   │   ├── settings_service.py       # Settings management
│   │   │   │   ├── snapshot_service.py       # Snapshot management
│   │   │   │   ├── staff_service.py          # Staff management
│   │   │   │   └── translation_service.py    # Translation service
│   │   ├── alembic/                   # Database migrations
│   │   │   ├── env.py                 # Alembic environment config
│   │   │   └── versions/              # Migration scripts
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── requirements.txt           # Python dependencies
│   │   ├── alembic.ini                # Alembic configuration
│   │   ├── docker-compose.yml         # Docker setup for PostgreSQL + Redis
│   │   └── Dockerfile                 # Container build config
│   └── main.py                        # Files directory entry point
│
├── discord-bot/                       # Discord moderation bot
│   ├── cogs/                          # Bot command modules
│   │   ├── ai_alerts.py               # AI-powered alerts
│   │   ├── ai_chat.py                 # AI chat integration
│   │   ├── ai_config.py               # AI configuration commands
│   │   ├── alt_alerts.py              # Alt account detection alerts
│   │   ├── announcements.py           # Announcement management
│   │   ├── chat_bridge.py             # Discord-Minecraft chat bridge
│   │   ├── events.py                  # Discord event handlers
│   │   ├── mc_commands.py             # Minecraft command execution
│   │   ├── moderation.py              # Moderation commands (18KB)
│   │   └── verification.py            # Player verification commands
│   ├── config.py                      # Bot configuration
│   ├── main.py                        # Bot entry point
│   └── requirements.txt               # Python dependencies
│
├── minecraft-plugin/                  # Paper Minecraft plugin
│   ├── src/main/java/                 # Java source code
│   │   └── com/umbrellaos/plugin/
│   │       └── api/
│   │           └── CoreApiClient.java # API client for umbrella-core
│   ├── src/main/resources/            # Plugin resources
│   ├── pom.xml                        # Maven build configuration
│   └── target/                        # Build output
│
├── docs/                              # Documentation
├── setup.sh                           # System setup script
├── start.sh                           # System startup script
├── fix_plugin.py                      # Plugin field name migration script
├── PHASE4_SUMMARY.md                  # Phase 4 documentation
├── PHASE5_SUMMARY.md                  # Phase 5 documentation
├── files.zip                          # Archived files
└── acli.exe                           # CLI executable
```

---

## Dependency Anchors

### Dashboard (Node.js/React)
| Package | Purpose |
|---------|---------|
| `@tanstack/react-query` | Server state management, caching |
| `next` | Full-stack React framework |
| `react` / `react-dom` | UI library |
| `recharts` | Data visualization |
| `shadcn` | UI component library |
| `lucide-react` | Icon system |
| `class-variance-authority` | Component variant handling |
| `clsx` / `tailwind-merge` | CSS class utilities |
| `next-themes` | Theme management |
| `sonner` | Toast notifications |
| `@vercel/analytics` | Analytics tracking |

### Umbrella Core (Python)
| Package | Purpose |
|---------|---------|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `sqlalchemy[asyncio]` | ORM with async support |
| `asyncpg` | Async PostgreSQL driver |
| `alembic` | Database migrations |
| `pydantic` / `pydantic-settings` | Data validation, config |
| `redis` / `aioredis` | Caching & sessions |
| `httpx` | HTTP client for external APIs |
| `python-multipart` | Multipart form parsing |

### Discord Bot (Python)
| Package | Purpose |
|---------|---------|
| `py-cord` | Discord bot framework |
| `httpx` | HTTP client |
| `python-dotenv` | Environment config |

### Minecraft Plugin (Java)
| Package | Purpose |
|---------|---------|
| `paper-api` | Minecraft server API |
| `ProtocolLib` | Packet manipulation |
| `okhttp` | HTTP client (shaded) |
| `gson` | JSON parsing (shaded) |

---

## Router Topology & API Endpoints

### Umbrella Core API Routes (FastAPI)

All routes mounted under `/api/v1/` prefix:

| Endpoint File | Route Path | Purpose |
|---------------|------------|---------|
| `auth.py` | `/auth/*` | Login, logout, session management |
| `health.py` | `/health` | Service health check |
| `settings.py` | `/settings` | System settings CRUD |
| `roles.py` | `/roles` | Role management |
| `audit.py` | `/audit` | Audit log queries |
| `players.py` | `/players` | Player data access |
| `punishments.py` | `/punishments` | Ban/kick/warn management |
| `appeals.py` | `/appeals` | Appeal system |
| `verification.py` | `/verification` | Player verification |
| `bridge.py` | `/bridge` | Discord-MC chat bridge |
| `mc_commands.py` | `/mc/commands` | Command execution |
| `plugin.py` | `/plugins` | Plugin management |
| `snapshot.py` | `/snapshots` | Player inventory snapshots |
| `replay.py` | `/replays` | Game replay data |
| `analytics.py` | `/analytics` | Statistics & metrics |
| `ai_config.py` | `/ai/config` | AI system configuration |
| `ai_tasks.py` | `/ai/tasks` | AI task queue |
| `alt_detection.py` | `/alts` | Alt account detection |
| `anticheat.py` | `/anticheat` | Anticheat integration |
| `staff.py` | `/staff` | Staff management |
| `translation.py` | `/translation` | Localization |
| `server_control.py` | `/server` | Server lifecycle control |
| `dashboard.py` | `/dashboard` | Dashboard meta-info |

### Dashboard Page Routes (Next.js)

| Page File | Route | Purpose |
|-----------|-------|---------|
| `page.tsx` | `/` | Landing page |
| `login/page.tsx` | `/login` | Authentication |
| `players/page.tsx` | `/players` | Player directory |
| `players/[uuid]/page.tsx` | `/players/:uuid` | Player profile |
| `punishments/page.tsx` | `/punishments` | Punishment manager |
| `appeals/page.tsx` | `/appeals` | Appeal queue |
| `servers/page.tsx` | `/servers` | Server status |
| `analytics/page.tsx` | `/analytics` | Analytics dashboard |
| `audit/page.tsx` | `/audit` | Audit logs |
| `alts/page.tsx` | `/alts` | Alt detection |
| `plugins/page.tsx` | `/plugins` | Plugin manager |
| `snapshots/page.tsx` | `/snapshots` | Snapshot viewer |
| `snapshots/[id]/page.tsx` | `/snapshots/:id` | Snapshot detail |
| `replay/page.tsx` | `/replay` | Replay viewer |
| `replay/[id]/page.tsx` | `/replay/:id` | Replay detail |
| `verification/page.tsx` | `/verification` | Player verification |
| `staff/page.tsx` | `/staff` | Staff management |
| `settings/page.tsx` | `/settings` | System settings |
| `announcements/page.tsx` | `/announcements` | Announcements |
| `ai-config/page.tsx` | `/ai-config` | AI configuration |
| `ai-tasks/page.tsx` | `/ai-tasks` | AI task management |
| `translation/page.tsx` | `/translation` | Translation management |
| `system/page.tsx` | `/system` | System status |

---

## Core Functions & State Index

### Backend Services (High-Impact)

| Service | File Location | Primary Function |
|---------|---------------|------------------|
| `SettingsService` | `files/umbrella-core/services/settings_service.py` | Global settings CRUD, default seeding |
| `RolesService` | `files/umbrella-core/services/roles_service.py` | Role/permission management |
| `AIService` | `files/umbrella-core/services/ai_service.py` | AI task execution, OpenRouter integration |
| `AltDetectionService` | `files/umbrella-core/services/alt_detection_service.py` | Alternate account correlation |
| `SnapshotService` | `files/umbrella-core/services/snapshot_service.py` | Player inventory snapshot management |
| `AnalyticsService` | `files/umbrella-core/services/analytics_service.py` | Statistical aggregation |
| `StaffService` | `files/umbrella-core/services/staff_service.py` | Staff member management |
| `DiscordService` | `files/umbrella-core/services/discord_service.py` | Discord API communication |

### Middleware (Request Pipeline)

| Middleware | File Location | Purpose |
|------------|---------------|---------|
| `auth.py` | `api/middleware/auth.py` | JWT/Bearer token validation |
| `permissions.py` | `api/middleware/permissions.py` | Role-based access control |
| `audit.py` | `api/middleware/audit.py` | Request audit logging |
| `session.py` | `api/middleware/session.py` | Session management |
| `errors.py` | `api/middleware/errors.py` | Global error handling |

### Database Models (Core Entities)

| Model | File Location | Key Fields |
|-------|---------------|------------|
| `Player` | `models/player.py` | uuid, username, minecraft_uuid, player_username, first_seen, last_seen |
| `User` | `models/user.py` | discord_id, username, role, permissions |
| `Punishment` | `models/punishment.py` | player_id, type, reason, expires_at, issued_by |
| `AuditLog` | `models/audit_log.py` | action, user_id, details, timestamp |
| `Snapshot` | `models/snapshot.py` | player_id, inventory, ender_chest, timestamp |
| `PluginCommand` | `models/plugin_command.py` | command, response, plugin_id |

### Dashboard State Management

| Hook/Module | File Location | Purpose |
|-------------|---------------|---------|
| `queries.ts` | `lib/queries.ts` | React Query hooks for all API endpoints |
| `api.ts` | `lib/api.ts` | Axios instance with interceptors |
| `auth-context.tsx` | `components/auth-context.tsx` | Authentication state provider |
| `types.ts` | `lib/types.ts` | TypeScript interfaces for API responses |

---

## AI Guardrails & Code Style

### TypeScript/JavaScript Conventions

**File Naming:**
- Components: `PascalCase.tsx` (e.g., `AddStaffDialog.tsx`)
- Utilities: `camelCase.ts` (e.g., `apiConfig.ts`)
- Pages: `page.tsx` in directory-based routing

**Indentation & Formatting:**
- Use 2 spaces for indentation (enforced by .editorconfig)
- Trailing commas in multi-line objects/arrays
- Single quotes for strings, except where template literals needed

**TypeScript Patterns:**
- Explicit return types for exported functions
- Interface over type for public APIs
- Use `readonly` for immutable arrays
- Strict null checking enabled in tsconfig

**React Patterns:**
- Functional components with TypeScript generics
- Prefer composition over inheritance
- Custom hooks for reusable stateful logic
- Memoization with `useMemo`/`useCallback` for expensive operations
- Error boundaries for component-level error handling

### Python Conventions (Umbrella Core & Discord Bot)

**Style:** PEP 8 with Black formatter

**File Naming:**
- Modules: `snake_case.py` (e.g., `settings_service.py`)
- Classes: `PascalCase` (e.g., `Settings`)
- Constants: `UPPER_SNAKE_CASE`

**Type Annotations:**
- Mandatory for function signatures and class attributes
- Use `from __future__ import annotations` for forward references

**Async Patterns:**
- Use `async`/`await` for all I/O operations
- Avoid blocking calls in request handlers
- Connection pooling via SQLAlchemy async session

**Dependency Injection:**
- FastAPI `Depends()` for request-scoped dependencies
- Service classes instantiated per-request

### Java Conventions (Minecraft Plugin)

**Style:** Standard Java conventions with Google Java Format

**File Naming:**
- Classes: `PascalCase.java` (e.g., `CoreApiClient.java`)
- Packages: lowercase, dot-separated (e.g., `com.umbrellaos.plugin.api`)

**Patterns:**
- Builder pattern for complex object construction
- Async callbacks for API calls via OkHttp
- ProtocolLib listeners for packet handling

### Git Workflow

**Commit Messages:**
- Use conventional commits format: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`
- Reference issue numbers in body when applicable

**Branch Naming:**
- Features: `feature/description`
- Bug fixes: `fix/description`
- Hotfixes: `hotfix/description`

### Testing Requirements

**Python:**
- Use `pytest` with `pytest-asyncio` for async tests
- Fixtures in `conftest.py` for common setup
- 80% coverage target for services

**TypeScript:**
- Jest or Vitest for unit tests
- Integration tests via React Testing Library

**Java:**
- JUnit 5 for unit tests
- Mockito for mocking

### Security Guidelines

**Secrets Management:**
- Never commit `.env` files; use `.env.example` as template
- Use environment variables for all credentials
- Rotate secrets regularly

**API Security:**
- Bearer token authentication on all endpoints except `/health`
- Rate limiting on authentication endpoints
- Input validation via Pydantic schemas (Python) and Zod (TypeScript)

**Database:**
- Parameterized queries via SQLAlchemy ORM
- Least privilege database user
- Regular backup schedule

---

## Architecture Overview

The UmbrellaMC system implements a microservices-style architecture with three primary communication channels:

1. **Dashboard ↔ Backend:** HTTP REST API (FastAPI backend, Next.js frontend)
2. **Discord Bot ↔ Backend:** HTTP REST API + Discord API (webhooks, bot commands)
3. **Minecraft Plugin ↔ Backend:** HTTP REST API (Java OkHttp client)

All components share a common PostgreSQL database via Umbrella Core, with Redis providing caching and session storage. The Discord bot acts as both a management interface and notification system, while the Minecraft plugin provides real-time server integration and player data collection.