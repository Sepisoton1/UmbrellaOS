# UmbrellaMC Auth System Report

## Auth Tiers

| Tier | Header | Validates | Used By |
|------|--------|-----------|---------|
| Plugin key | `X-Plugin-Key` | `SECRET_KEY` | Plugin heartbeat, anticheat |
| Admin key | `X-Admin-Key` | `ADMIN_KEY` | Bot, plugin, bootstrap |
| Session | `Authorization: Bearer` | `sessions` table | Dashboard OAuth users |

**Note:** `require_plugin_key` also accepts `X-Admin-Key` as fallback.

## Discord OAuth Flow

```
Dashboard → POST /auth/discord/authorize → Discord OAuth URL
Discord → redirect /login?code&state
Dashboard → POST /auth/discord/callback → { token, user, expires_in }
Dashboard → localStorage['umbrella_token']
Dashboard → GET /auth/me (Bearer) → user + role + permissions
```

### First User Bootstrap

- First OAuth user automatically receives `owner` role
- `INITIAL_ADMIN_DISCORD_ID` env var can also grant owner on first login

### Session Model

- 7-day expiry
- Stored in `sessions` table with `revoked` flag
- **Fixed:** `is_valid()` now uses timezone-aware comparison

## `/auth/me` Response (Enriched)

```json
{
  "id": "uuid",
  "discord_id": "123456789",
  "username": "StaffName",
  "email": "user@example.com",
  "role_id": "role-uuid",
  "role": "admin",
  "permissions": ["players.view", "punishments.view", ...],
  "is_active": true,
  "created_at": "...",
  "updated_at": "..."
}
```

## Dashboard Auth Chain

```
Providers → AuthProvider → AuthGuard → ConditionalShell → AppShell
```

| Route | Auth Behavior |
|-------|---------------|
| `/login` | Bypass guard |
| `/no-access` | Bypass guard (no role_id) |
| All others | Require token + user with role_id |

## API Config Fix

```typescript
// Supports both http://host and http://host/api/v1 env values
API_ROOT  → base without /api/v1 (for /health)
API_V1    → versioned prefix (for all API calls)
```

## Security Findings & Fixes

| Issue | Severity | Status |
|-------|----------|--------|
| CORS `*` + `credentials: true` | Medium | **Fixed** → `credentials: false` |
| Session timezone bug | Medium | **Fixed** |
| `user.role` never populated | High | **Fixed** |
| Logout accepts token in query | Low | Open (intentional for now) |
| No Next.js middleware | Medium | Open |
| Admin key god mode | By design | Documented |
| Public appeal creation | By design | Rate limit recommended |

## Test Infrastructure Fix

`conftest.py` now patches both `secret_key` and `admin_key`, plus module-level `settings` in auth/session middleware — **200/200 tests passing**.

## Dual-Key Configuration

```env
SECRET_KEY=...    # Plugin authentication
ADMIN_KEY=...     # Dashboard/bot authentication
```

Plugin `config.yml` uses `admin_key` field. Ensure keys match deployment expectations.
