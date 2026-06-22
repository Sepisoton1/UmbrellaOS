# UmbrellaMC Permission System Report

## Overview

Umbrella Core uses **role-based access control (RBAC)** with 16 seeded permission keys, 5 roles, and per-user `extra_permissions` overrides.

**Active implementation:** `api/dependencies/permissions.py`  
**Removed (dead):** `api/middleware/permissions.py`

## Permission Keys (16)

```
players.view, players.manage
punishments.view, punishments.create, punishments.revoke
appeals.view, appeals.manage
moderation.kick, moderation.warn, moderation.ban, moderation.ipban
settings.view, settings.manage
audit.view
roles.manage
server.control
```

## Role Matrix

| Permission | owner | admin | moderator | helper | member |
|------------|:-----:|:-----:|:---------:|:------:|:------:|
| players.view | ✓ | ✓ | ✓ | ✓ | |
| players.manage | ✓ | ✓ | ✓ | | |
| punishments.view | ✓ | ✓ | ✓ | ✓ | |
| punishments.create | ✓ | ✓ | ✓ | | |
| punishments.revoke | ✓ | ✓ | ✓ | | |
| appeals.view | ✓ | ✓ | ✓ | ✓ | ✓ |
| appeals.manage | ✓ | ✓ | ✓ | | |
| moderation.* | ✓ | ✓ | ✓ | partial | |
| settings.view | ✓ | ✓ | | | |
| settings.manage | ✓ | ✓ | | | |
| audit.view | ✓ | ✓ | | | |
| roles.manage | ✓ | | | | |
| server.control | ✓ | ✓ | | | |

## Enforcement Mechanisms

### Backend

```python
require_permission("players.view")     # Single permission
RoleChecker(["a", "b"], require_all=False)  # Any-of
require_owner()                        # Owner role or admin key
```

**Admin key bypass:** `X-Admin-Key` matching `ADMIN_KEY` bypasses all RBAC checks (service-to-service).

**Extra permissions:** `User.extra_permissions` JSON array is now merged into effective permissions at check time.

### Dashboard

| Layer | Enforcement | Status |
|-------|-------------|--------|
| `AuthGuard` | Requires token + `role_id` | ✓ Working |
| `AppSidebar` | Filters by `user.role` | ✓ Fixed (role now in `/auth/me`) |
| Page-level guards | None | ⚠️ URL-direct access possible |
| `global-search` | No role filter | ⚠️ Hidden routes discoverable |
| API calls | Backend RBAC | ✓ Working |

### Discord Bot

Separate Discord role hierarchy (not Core RBAC):

```
helper → moderator → admin → owner
```

Commands gated via `can_use(member, command)` and `USER_PERMISSION_OVERRIDES`.

## Reconstruction Changes

1. Migrated dashboard GET endpoints from `require_admin_key` to `require_permission()`:
   - analytics, audit, replay, snapshot, ai_tasks, ai_config, translation
2. Staff/roles list uses `RoleChecker` for session users with `players.view`
3. `/auth/me` returns `role` + `permissions[]` for dashboard nav
4. `extra_permissions` on User model now enforced
5. Deleted duplicate `api/middleware/permissions.py`

## Known Gaps

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No `audit.view` on helper | Helpers can't see audit | By design |
| Dashboard page guards missing | Direct URL access | Add permission-aware route wrapper |
| Discord vs Core RBAC split | Two permission systems | Document mapping table |
| `audit.view` unused in old code | Was admin-key only | Fixed in this pass |
| Member role minimal access | Only appeals.view | Intentional for appeal-only users |

## Dashboard Nav Role Gates

| Page | Required Role |
|------|---------------|
| AI Config | admin, owner |
| Audit Log | admin, owner |
| Settings | owner |
| All others | Any authenticated staff |
