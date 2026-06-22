"""
cogs/moderation.py — Staff moderation commands with role-based permissions.

Role hierarchy:
  helper    -> warn, lookup, history
  moderator -> + kick, mute, unmute, tempban
  admin     -> + ban, unban, broadcast
  owner     -> everything
"""
import httpx
import discord
from discord.ext import commands
from discord import option
from config import config

ROLE_HIERARCHY = ["helper", "moderator", "admin", "owner"]

ROLE_PERMISSIONS = {
    "helper":    ["warn", "lookup", "history", "staff"],
    "moderator": ["warn", "lookup", "history", "staff", "kick", "mute", "unmute", "tempban"],
    "admin":     ["warn", "lookup", "history", "staff", "kick", "mute", "unmute", "tempban", "ban", "unban", "broadcast"],
    "owner":     ["warn", "lookup", "history", "staff", "kick", "mute", "unmute", "tempban", "ban", "unban", "broadcast"],
}


def get_member_rank(member: discord.Member) -> str | None:
    role_names = [r.name.lower() for r in member.roles]
    for rank in reversed(ROLE_HIERARCHY):
        if rank in role_names:
            return rank
    return None


# Per-user permission overrides. Use this to grant ONE specific person
# extra commands without changing their Discord role or rank.
# Keys are Discord user IDs (int), values are lists of command names
# from the same set used in ROLE_PERMISSIONS (or "moonbrain", once wired
# in below).
USER_PERMISSION_OVERRIDES: dict[int, list[str]] = {
    # 123456789012345678: ["mute", "warn"],
}


def can_use(member: discord.Member, command: str) -> bool:
    rank = get_member_rank(member)
    role_allowed = rank is not None and command in ROLE_PERMISSIONS.get(rank, [])
    override_allowed = command in USER_PERMISSION_OVERRIDES.get(member.id, [])
    return role_allowed or override_allowed


async def api_get(path: str) -> dict | list | None:
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                f"{config.UMBRELLA_API_URL}{path}",
                headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
            )
            return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"[Moderation] GET {path} error: {e}")
        return None


async def api_post(path: str, body: dict) -> tuple[int, dict]:
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(
                f"{config.UMBRELLA_API_URL}{path}",
                headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
                json=body,
            )
            return r.status_code, r.json()
    except Exception as e:
        print(f"[Moderation] POST {path} error: {e}")
        return 500, {"error": str(e)}


async def find_player(username: str) -> dict | None:
    data = await api_get(f"/api/v1/players?search={username}&limit=1")
    if data and len(data) > 0:
        return data[0]
    return None


def punishment_embed(title: str, player: str, reason: str, moderator: str, color: discord.Color, extra: str = "") -> discord.Embed:
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="Player", value=player, inline=True)
    embed.add_field(name="Moderator", value=moderator, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    if extra:
        embed.add_field(name="Duration", value=extra, inline=True)
    return embed


class Moderation(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # ── /warn ──────────────────────────────────────────────────────────────
    @commands.slash_command(name="warn", description="Warn a player")
    @option("player", description="Minecraft username")
    @option("reason", description="Reason for warning")
    async def warn(self, ctx: discord.ApplicationContext, player: str, reason: str):
        if not can_use(ctx.author, "warn"):
            await ctx.respond("❌ You need at least **Helper** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        status, resp = await api_post("/api/v1/punishments", {
            "player_uuid": p["uuid"], "type": "warn", "reason": reason,
            "issued_by_discord_id": str(ctx.author.id),
        })
        if status in (200, 201):
            await ctx.followup.send(embed=punishment_embed("⚠️ Player Warned", p["username"], reason, ctx.author.display_name, discord.Color.yellow()))
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /kick ───────────────────────────────────────────────────────────────
    @commands.slash_command(name="kick", description="Kick a player from the server")
    @option("player", description="Minecraft username")
    @option("reason", description="Reason for kick")
    async def kick(self, ctx: discord.ApplicationContext, player: str, reason: str):
        if not can_use(ctx.author, "kick"):
            await ctx.respond("❌ You need at least **Moderator** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        status, resp = await api_post("/api/v1/mc/command", {
            "command": f"kick {p['username']} {reason}",
            "requested_by_discord_id": str(ctx.author.id),
            "requested_by_username": ctx.author.display_name,
        })
        if status in (200, 201):
            await ctx.followup.send(embed=punishment_embed("👢 Player Kicked", p["username"], reason, ctx.author.display_name, discord.Color.orange()))
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /mute ───────────────────────────────────────────────────────────────
    @commands.slash_command(name="mute", description="Mute a player")
    @option("player", description="Minecraft username")
    @option("reason", description="Reason for mute")
    @option("duration_hours", description="Duration in hours (0 = permanent)", required=False)
    async def mute(self, ctx: discord.ApplicationContext, player: str, reason: str, duration_hours: int = 0):
        if not can_use(ctx.author, "mute"):
            await ctx.respond("❌ You need at least **Moderator** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        body = {"player_uuid": p["uuid"], "type": "mute", "reason": reason, "issued_by_discord_id": str(ctx.author.id)}
        if duration_hours > 0:
            import datetime
            body["expires_at"] = (datetime.datetime.utcnow() + datetime.timedelta(hours=duration_hours)).isoformat() + "Z"
        status, resp = await api_post("/api/v1/punishments", body)
        if status in (200, 201):
            dur = f"{duration_hours}h" if duration_hours > 0 else "Permanent"
            await ctx.followup.send(embed=punishment_embed("🔇 Player Muted", p["username"], reason, ctx.author.display_name, discord.Color.greyple(), dur))
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /unmute ─────────────────────────────────────────────────────────────
    @commands.slash_command(name="unmute", description="Unmute a player")
    @option("player", description="Minecraft username")
    async def unmute(self, ctx: discord.ApplicationContext, player: str):
        if not can_use(ctx.author, "unmute"):
            await ctx.respond("❌ You need at least **Moderator** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        punishments = await api_get(f"/api/v1/punishments?player_uuid={p['uuid']}&active_only=true")
        mute = next((x for x in (punishments or []) if x.get("type") == "mute"), None)
        if not mute:
            await ctx.followup.send(f"❌ `{player}` is not muted."); return
        status, resp = await api_post(f"/api/v1/punishments/{mute['id']}/revoke", {})
        if status in (200, 201):
            await ctx.followup.send(f"🔊 **{p['username']}** has been unmuted.")
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /tempban ─────────────────────────────────────────────────────────────
    @commands.slash_command(name="tempban", description="Temporarily ban a player")
    @option("player", description="Minecraft username")
    @option("duration_hours", description="Duration in hours")
    @option("reason", description="Reason for ban")
    async def tempban(self, ctx: discord.ApplicationContext, player: str, duration_hours: int, reason: str):
        if not can_use(ctx.author, "tempban"):
            await ctx.respond("❌ You need at least **Moderator** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        import datetime
        body = {
            "player_uuid": p["uuid"], "type": "tempban", "reason": reason,
            "issued_by_discord_id": str(ctx.author.id),
            "expires_at": (datetime.datetime.utcnow() + datetime.timedelta(hours=duration_hours)).isoformat() + "Z",
        }
        status, resp = await api_post("/api/v1/punishments", body)
        if status in (200, 201):
            await ctx.followup.send(embed=punishment_embed("⏳ Player Temp Banned", p["username"], reason, ctx.author.display_name, discord.Color.red(), f"{duration_hours}h"))
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /ban ─────────────────────────────────────────────────────────────────
    @commands.slash_command(name="ban", description="Permanently ban a player")
    @option("player", description="Minecraft username")
    @option("reason", description="Reason for ban")
    async def ban(self, ctx: discord.ApplicationContext, player: str, reason: str):
        if not can_use(ctx.author, "ban"):
            await ctx.respond("❌ You need at least **Admin** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        status, resp = await api_post("/api/v1/punishments", {
            "player_uuid": p["uuid"], "type": "ban", "reason": reason,
            "issued_by_discord_id": str(ctx.author.id),
        })
        if status in (200, 201):
            await ctx.followup.send(embed=punishment_embed("🔨 Player Banned", p["username"], reason, ctx.author.display_name, discord.Color.dark_red()))
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /unban ───────────────────────────────────────────────────────────────
    @commands.slash_command(name="unban", description="Unban a player")
    @option("player", description="Minecraft username")
    async def unban(self, ctx: discord.ApplicationContext, player: str):
        if not can_use(ctx.author, "unban"):
            await ctx.respond("❌ You need at least **Admin** to use this.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        punishments = await api_get(f"/api/v1/punishments?player_uuid={p['uuid']}&active_only=true")
        ban = next((x for x in (punishments or []) if x.get("type") in ("ban", "tempban")), None)
        if not ban:
            await ctx.followup.send(f"❌ `{player}` is not banned."); return
        status, resp = await api_post(f"/api/v1/punishments/{ban['id']}/revoke", {})
        if status in (200, 201):
            await ctx.followup.send(f"✅ **{p['username']}** has been unbanned.")
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")

    # ── /lookup ──────────────────────────────────────────────────────────────
    @commands.slash_command(name="lookup", description="Look up a player")
    @option("player", description="Minecraft username")
    async def lookup(self, ctx: discord.ApplicationContext, player: str):
        if not can_use(ctx.author, "lookup"):
            await ctx.respond("❌ Staff only.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        embed = discord.Embed(title=f"🔍 {p['username']}", color=discord.Color.blurple())
        embed.add_field(name="UUID", value=p.get("uuid", "N/A"), inline=False)
        embed.add_field(name="Status", value=p.get("status", "unknown").capitalize(), inline=True)
        embed.add_field(name="First Seen", value=str(p.get("first_seen", "N/A"))[:10], inline=True)
        embed.add_field(name="Last Seen", value=str(p.get("last_seen", "N/A"))[:10], inline=True)
        embed.add_field(name="Playtime", value=f"{round(p.get('playtime', 0) / 3600, 1)}h", inline=True)
        embed.add_field(name="Discord", value=p.get("discord_id") or "Not linked", inline=True)
        await ctx.followup.send(embed=embed)

    # ── /history ─────────────────────────────────────────────────────────────
    @commands.slash_command(name="history", description="View punishment history for a player")
    @option("player", description="Minecraft username")
    async def history(self, ctx: discord.ApplicationContext, player: str):
        if not can_use(ctx.author, "history"):
            await ctx.respond("❌ Staff only.", ephemeral=True); return
        await ctx.defer()
        p = await find_player(player)
        if not p:
            await ctx.followup.send(f"❌ Player `{player}` not found."); return
        punishments = await api_get(f"/api/v1/punishments?player_uuid={p['uuid']}&active_only=false&limit=10")
        if not punishments:
            await ctx.followup.send(f"✅ `{player}` has no punishment history."); return
        embed = discord.Embed(title=f"📋 Punishment History — {p['username']}", color=discord.Color.blurple())
        for pun in punishments:
            status = "✅ Active" if pun.get("active") else "❌ Revoked"
            embed.add_field(
                name=f"{pun.get('type','?').upper()} — {status}",
                value="**Reason:** " + str(pun.get("reason","N/A")) + "\n**Date:** " + str(pun.get("created_at",""))[:10],
                inline=False,
            )
        await ctx.followup.send(embed=embed)

    # ── /staff ────────────────────────────────────────────────────────────────
    @commands.slash_command(name="staff", description="List current staff members")
    async def staff(self, ctx: discord.ApplicationContext):
        if not can_use(ctx.author, "staff"):
            await ctx.respond("❌ Staff only.", ephemeral=True); return
        await ctx.defer()
        data = await api_get("/api/v1/auth?limit=100")
        if not data:
            await ctx.followup.send("❌ Could not fetch staff list."); return
        embed = discord.Embed(title="👥 Staff Members", color=discord.Color.green())
        for member in data:
            embed.add_field(
                name=member.get("username", "Unknown"),
                value=f"Discord: <@{member['discord_id']}>" if member.get("discord_id") else "No Discord",
                inline=True,
            )
        await ctx.followup.send(embed=embed)

    # ── /broadcast ────────────────────────────────────────────────────────────
    @commands.slash_command(name="broadcast", description="Send a message in-game to all players")
    @option("message", description="Message to broadcast")
    async def broadcast(self, ctx: discord.ApplicationContext, message: str):
        if not can_use(ctx.author, "broadcast"):
            await ctx.respond("❌ You need at least **Admin** to use this.", ephemeral=True); return
        await ctx.defer()
        status, resp = await api_post("/api/v1/mc/command", {
            "command": f"say {message}",
            "requested_by_discord_id": str(ctx.author.id),
            "requested_by_username": ctx.author.display_name,
        })
        if status in (200, 201):
            await ctx.followup.send(f"📢 Broadcast sent: `{message}`")
        else:
            await ctx.followup.send(f"❌ Failed: {resp.get('detail', resp)}")


def setup(bot: discord.Bot):
    bot.add_cog(Moderation(bot))
