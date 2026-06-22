# Dashboard Refactor Report

## Scope

24 App Router pages, React Query hooks, auth layer, API client, transforms, and navigation.

## Critical Fixes Applied

### 1. API URL Resolution (`lib/api-config.ts`)

**Problem:** `API_ROOT` and `API_V1` were identical; `/health` returned 404 when env pointed to `/api/v1`.

**Fix:** Derive `API_ROOT` by stripping `/api/v1` suffix; health checks hit correct path.

### 2. Auth Role Population

**Problem:** `/auth/me` returned only `role_id`; sidebar role gates never worked.

**Fix:** Backend now returns `role` + `permissions`; sidebar compares lowercase role names.

### 3. System Health Page Mapping

**Problem:** `mapHealth()` returned `cpuPercent` but page expected `cpuPct`, `connections` vs `activeConnections`, component `name` vs `id`/`label`.

**Fix:** Aligned `SystemMetrics` transform to page contract.

### 4. React Query Cache Invalidation

**Fix:** Punishment/appeal mutations now invalidate `dashboard` and `player-punishments` keys; false-positive invalidates `flagged-players`.

### 5. Replay Event Filters

**Fix:** `getReplayEvents()` now passes `event_type` and `minecraft_uuid` query params.

### 6. Alts False Positive

**Problem:** Hardcoded `event_id: 0`.

**Fix:** API accepts `player_uuid`; page passes player UUID + staff username.

### 7. Add Staff Dialog

**Problem:** Filtered roles by `r.name` but `RoleDefinition` uses `role`.

**Fix:** Use `r.role` consistently.

### 8. Login Build Error

**Problem:** `useSearchParams()` without Suspense boundary.

**Fix:** Split into `LoginContent` wrapped in `<Suspense>`.

### 9. Alts Page UX

**Fix:** `Button asChild` + `Link` for valid HTML; removed nested interactive elements.

## Route Map (All 24 Routes)

| Route | Backend Integration | Status |
|-------|---------------------|--------|
| `/` | punishments, appeals, analytics/summary | ✓ |
| `/players` | `/players` | ✓ |
| `/players/[uuid]` | player, punishments, appeals | ✓ |
| `/analytics` | analytics/* | ✓ |
| `/replay` | replay/sessions | ✓ |
| `/replay/[id]` | replay session + events | ✓ |
| `/snapshots` | snapshots by UUID | ✓ |
| `/snapshots/[id]` | snapshot detail | ✓ |
| `/ai-tasks` | ai/tasks | ✓ |
| `/ai-config` | ai/config/* | ✓ |
| `/punishments` | punishments CRUD | ✓ |
| `/appeals` | appeals | ✓ |
| `/staff` | auth + roles + staff | ✓ |
| `/verification` | verification/pending | ✓ |
| `/alts` | alts/* | ✓ |
| `/servers` | dashboard/servers | ✓ |
| `/plugins` | dashboard/plugins | ✓ |
| `/announcements` | settings | ✓ |
| `/translation` | translation/language/all | ✓ |
| `/system` | /health | ✓ |
| `/audit` | audit | ✓ |
| `/settings` | settings + bridge | ✓ |
| `/login` | OAuth | ✓ |
| `/no-access` | auth only | ✓ |

## Build Validation

```
npm run build → ✓ 23/23 pages generated
```

## Remaining Recommendations

1. Add Next.js `middleware.ts` for server-side auth redirect
2. Add page-level permission guards using `user.permissions`
3. Filter `global-search` nav items by role
4. Wire `useConnectionTest` to sidebar footer
5. Remove hardcoded notifications in `top-bar.tsx`
6. Enrich `mapPlayer()` with IPs, punishment count from detail endpoint
7. Add `useApproveAITask`/`useDenyAITask` mutation hooks with invalidation

## Performance Settings

```typescript
// providers.tsx
staleTime: 300_000 (5 min)
refetchOnWindowFocus: false
retry: 1

// Polling intervals
plugins: 5s, system-health: 5s, dashboard: 5min
```
