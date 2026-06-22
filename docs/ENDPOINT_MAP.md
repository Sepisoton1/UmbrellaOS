# UmbrellaMC Endpoint Map

**Base URL:** `{HOST}/api/v1`  
**Health:** `{HOST}/health` (no auth, not under `/api/v1`)

## Authentication Legend

| Symbol | Meaning |
|--------|---------|
| 🔓 | Public |
| 🔑 | `X-Admin-Key` or `X-Plugin-Key` |
| 🎫 | Bearer session token |
| 👤 | RBAC permission (session or admin key bypass) |

---

## Root & Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | 🔓 | Service info |
| GET | `/health` | 🔓 | DB connectivity check |

## Auth `/api/v1/auth`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 `roles.manage` OR `players.view` | List staff users |
| GET | `/users/{id}` | 🔑 | Get user by ID |
| POST | `/users` | 🔑 | Create staff user |
| PATCH | `/users/{id}` | 🔑 | Update user |
| DELETE | `/users/{id}` | 🔑 | Deactivate user |
| POST | `/discord/authorize` | 🔓 | Start OAuth |
| POST | `/discord/callback` | 🔓 | OAuth callback |
| POST | `/logout` | 🎫 query | Revoke session |
| GET | `/me` | 🎫 | Current user + role + permissions |

## Settings `/api/v1/settings`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 owner | List settings (masked) |
| GET | `/{key}` | 👤 owner | Get setting (sensitive always masked) |
| PATCH | `/{key}` | 👤 owner | Update setting |

## Roles `/api/v1/roles`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 `roles.manage` OR `players.view` | List roles |
| GET | `/permissions` | 👤 `roles.manage` OR `players.view` | List permission keys |

## Players `/api/v1/players`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 `players.view` | List players |
| GET | `/{uuid}` | 👤 `players.view` | Player detail |

## Punishments `/api/v1/punishments`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 `punishments.view` | List punishments |
| POST | `` | 👤 `punishments.create` | Create punishment |
| PATCH | `/{id}` | 👤 `punishments.create` | Update punishment |
| POST | `/{id}/revoke` | 👤 `punishments.revoke` | Revoke punishment |

## Appeals `/api/v1/appeals`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 `appeals.view` | List appeals |
| POST | `` | 🔓 | Create appeal (public) |
| PATCH | `/{id}` | 👤 `appeals.manage` | Update appeal status |

## Moderation `/api/v1/moderation`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/kick` | 👤 `moderation.kick` | Kick player |
| POST | `/warn` | 👤 `moderation.warn` | Warn player |
| POST | `/ban` | 👤 `moderation.ban` | Ban player |
| POST | `/unban` | 👤 `moderation.ban` | Unban player |
| POST | `/ipban` | 👤 `moderation.ipban` | IP ban |
| POST | `/ipunban` | 👤 `moderation.ipban` | IP unban |
| GET | `/active/{uuid}` | 👤 `punishments.view` | Active punishments |

## Bridge `/api/v1/bridge`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/message` | 🔑 | Post bridge message |
| GET | `/messages` | 👤 `players.view` | Poll messages |
| GET | `/settings` | 👤 `settings.view` | Bridge settings |
| PATCH | `/settings` | 👤 `settings.manage` | Update bridge settings |

## Verification `/api/v1/verification`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/request` | 🔑 | Request verify code |
| POST | `/confirm` | 🔑 | Confirm code |
| POST | `/status` | 🔑 | Check verified status |
| GET | `/pending` | 👤 `players.view` | Pending verifications |
| POST | `/revoke` | 👤 `players.manage` | Revoke verification |
| POST | `/manual-link` | 🔑 | Staff manual link |
| DELETE | `/unlink/{discord_id}` | 🔑 | Unlink Discord |
| POST | `/resolve-pending` | 🔑 | Resolve pending link |

## Alt Detection `/api/v1/alts`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/check` | 🔑 | Check player suspicion |
| GET | `/flagged` | 👤 `players.view` | Flagged players |
| GET | `/player/{uuid}` | 👤 `players.view` | Player suspicion history |
| POST | `/false-positive` | 👤 `players.manage` | Mark false positive |
| POST | `/group` | 👤 `players.manage` | Create alt group |
| GET | `/groups` | 👤 `players.view` | List alt groups |

## Analytics `/api/v1/analytics`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/events` | 🔑 | Record event (plugin) |
| GET | `/events` | 👤 `players.view` | List events |
| GET | `/players/{uuid}` | 👤 `players.view` | Player stats |
| GET | `/summary` | 👤 `players.view` | Server summary |

## Replay `/api/v1/replay`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/sessions` | 🔑 | Create session (plugin) |
| GET | `/sessions` | 👤 `players.view` | List sessions |
| GET | `/sessions/{id}` | 👤 `players.view` | Get session |
| POST | `/sessions/{id}/events` | 🔑 | Ingest events |
| POST | `/sessions/{id}/finalize` | 🔑 | Finalize session |
| GET | `/sessions/{id}/events` | 👤 `players.view` | Get events |

## Snapshots `/api/v1/snapshots`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `` | 🔑 | Create snapshot (plugin) |
| GET | `/players/{uuid}` | 👤 `players.view` | List snapshots |
| GET | `/players/{uuid}/latest` | 👤 `players.view` | Latest snapshot |
| GET | `/{id}` | 👤 `players.view` | Get snapshot |
| GET | `/replay/{replay_id}` | 👤 `players.view` | Snapshots near replay |

## AI Tasks `/api/v1/ai`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/review/player/{uuid}` | 🔑 | Trigger player review |
| POST | `/review/appeal/{id}` | 🔑 | Trigger appeal review |
| GET | `/tasks` | 👤 `punishments.view` | List AI tasks |
| GET | `/tasks/{id}` | 👤 `punishments.view` | Get AI task |
| POST | `/tasks/{id}/approve` | 👤 `punishments.create` | Approve task |
| POST | `/tasks/{id}/deny` | 👤 `punishments.create` | Deny task |

## AI Config `/api/v1/ai/config`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/request` | 👤 `settings.manage` | Request AI config |
| GET | `/pending` | 👤 `settings.manage` | Pending configs |
| POST | `/{id}/approve` | 👤 `settings.manage` | Approve config |
| POST | `/{id}/reject` | 👤 `settings.manage` | Reject config |

## MC Commands `/api/v1/mc`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/command` | 🔑 | Queue console command |
| GET | `/commands/pending` | 🔑 | Poll pending commands |
| POST | `/commands/{id}/complete` | 🔑 | Complete command |

## Translation `/api/v1/translation`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/language` | 🔑 | Set player language |
| GET | `/language/all` | 👤 `players.view` | All languages |
| GET | `/language/{uuid}` | 👤 `players.view` | Player language |
| POST | `/translate` | 🔑 | Translate message |

## Anticheat `/api/v1/anticheat`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/flag` | 🔑 plugin | Report cheat flag |

## Dashboard `/api/v1/dashboard`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/servers` | 👤 `players.view` | Server list |
| GET | `/plugins` | 👤 `players.view` | Plugin heartbeats |

## Server Control `/api/v1/server`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/control` | 👤 `server.control` | Server power/restart |

## Staff `/api/v1/staff`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/manage` | 👤 `roles.manage` | Promote/demote |
| POST | `/add` | 👤 `roles.manage` | Add staff |
| GET | `/discord-members` | 👤 `roles.manage` | Discord members |

## Plugin `/api/v1/plugin`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | 🔑 plugin | Plugin health check |
| POST | `/heartbeat` | 🔑 plugin | Server heartbeat |
| GET | `/config` | 🔑 plugin | Plugin config bundle |
| POST | `/control` | 🔑 plugin | Queue plugin control |

## Audit `/api/v1/audit`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `` | 👤 `audit.view` | Paginated audit log |
| GET | `/{action}` | 👤 `audit.view` | Filter by action |

---

**Total:** ~105 endpoints across 25 routers
