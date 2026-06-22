"""
cogs/ai_chat.py — MOON AI chat, model auto-selection, and owner natural-language
command executor.

Ported from the original Umbrella-Bot monolith (main1.py) and adapted to MOON's
existing async/cog architecture. Reuses helpers already defined in
cogs/moderation.py (api_post, api_get, find_player, get_member_rank) instead of
duplicating them, and routes the natural-language "/moonbrain" command through
MOON's existing moderation actions rather than raw RCON (MOON has no RCON —
everything goes through the Core API, same as every other staff command).

Setup required:
  1. Add to discord-bot/.env:
       OPENROUTER_API_KEY=sk-or-v1-...
  2. Load this cog in main.py's extension list, e.g.:
       for ext in (..., "cogs.moderation", "cogs.ai_chat"):
  3. cogs.moderation must already be loaded (this cog imports helpers from it).
"""
import re
import json
import time
from collections import defaultdict

import httpx
import discord
from discord.ext import commands
from discord import option

from cogs.moderation import (
    get_member_rank,
    can_use,
    api_get,
    api_post,
    find_player,
)
from settings_client import get_setting

# ── Config ───────────────────────────────────────────────────────────────────
# OPENROUTER_API_KEY now comes from the dashboard (Settings -> ai.openrouter_key),
# fetched via settings_client, NOT from this bot's own .env. One source of truth.
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

PLACEHOLDER_VALUES = {"", "sk-or-v1-your-openrouter-key", "YOUR_OPENROUTER_KEY_HERE"}

FREE_MODEL_PRIORITY = [
    "openai/gpt-oss-20b:free",
    "openai/gpt-oss-120b:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder:free",
]

# Module-level state (mirrors the original bot's pattern — simple, no DB needed)
AI_MODEL = "auto"
AI_MODEL_LOCKED = False
AI_MEMORY: dict[int, list] = defaultdict(list)
AI_LAST_USED: dict[int, float] = {}
MAX_HISTORY = 8
MEMORY_TIMEOUT = 900  # seconds of inactivity before a user's chat memory resets

# Action vocabulary for the owner natural-language command. Deliberately scoped
# to MOON's existing, already-audited moderation actions — no raw command
# passthrough, no arbitrary backend writes.
ACTION_DESCRIPTIONS = (
    '{"action":"ban|kick|mute|tempban|warn|unban|broadcast|none",'
    '"player":"<minecraft username, omit for broadcast/none>",'
    '"reason":"...",'
    '"duration_hours":<int, only for mute/tempban, omit otherwise>,'
    '"message":"<only for broadcast>"}'
)


async def is_ai_configured() -> bool:
    key = await get_setting("ai.openrouter_key")
    return key not in PLACEHOLDER_VALUES


async def select_best_free_model() -> str:
    """Ask OpenRouter what's currently available and pick the best free model
    from our priority list, falling back to any free model if none match."""
    global AI_MODEL
    key = await get_setting("ai.openrouter_key")
    if key in PLACEHOLDER_VALUES:
        return AI_MODEL
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                OPENROUTER_MODELS_URL,
                headers={"Authorization": f"Bearer {key}"},
            )
            r.raise_for_status()
            available = {m["id"] for m in r.json().get("data", []) if m.get("id")}
        for model_id in FREE_MODEL_PRIORITY:
            if model_id in available:
                AI_MODEL = model_id
                return AI_MODEL
        free_models = sorted(m for m in available if ":free" in m)
        if free_models:
            AI_MODEL = free_models[0]
            return AI_MODEL
    except Exception as e:
        print(f"[AI] Model selection failed: {e}")
    return AI_MODEL


async def query_ai(system_prompt: str, user_message: str, history: list | None = None, max_tokens: int = 512) -> str:
    """Call OpenRouter with automatic fallback across free models if the
    current one is rate-limited, unavailable, or errors out."""
    global AI_MODEL
    key = await get_setting("ai.openrouter_key")
    if key in PLACEHOLDER_VALUES:
        return "⚠️ AI is not configured. Set the OpenRouter key in Dashboard → Settings → AI."

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/MOON",
        "X-Title": "MOON",
    }
    model = AI_MODEL if AI_MODEL != "auto" else FREE_MODEL_PRIORITY[0]
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {"model": model, "max_tokens": max_tokens, "messages": messages}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(OPENROUTER_URL, headers=headers, json=payload)

            if r.status_code in (400, 404, 429, 502, 503) and not AI_MODEL_LOCKED:
                for fallback in FREE_MODEL_PRIORITY:
                    if fallback == payload["model"]:
                        continue
                    payload["model"] = fallback
                    r = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                    if r.status_code == 200:
                        AI_MODEL = fallback
                        break

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except httpx.TimeoutException:
        return "⚠️ AI timed out. Try again shortly."
    except httpx.HTTPStatusError as e:
        print(f"[AI] OpenRouter HTTP error: {e.response.status_code} — {e.response.text[:200]}")
        return f"⚠️ AI service error ({e.response.status_code}). Try `/aimodel refresh`."
    except (KeyError, IndexError):
        return "⚠️ AI response was malformed."
    except Exception as e:
        print(f"[AI] OpenRouter error: {e}")
        return "⚠️ Unexpected AI error."


class AIChat(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def cog_load(self):
        # Runs once the bot's event loop is actually running — safer than
        # scheduling a task at import time before bot.run() has started.
        await select_best_free_model()

    # ── /ask ───────────────────────────────────────────────────────────────
    @commands.slash_command(name="ask", description="Ask MOON's AI a question")
    @option("question", description="Your question about the server, rules, or anything else")
    async def ask(self, ctx: discord.ApplicationContext, question: str):
        await ctx.defer()

        rank = get_member_rank(ctx.author) if isinstance(ctx.author, discord.Member) else None
        user_id = ctx.author.id
        now = time.time()
        if now - AI_LAST_USED.get(user_id, 0) > MEMORY_TIMEOUT:
            AI_MEMORY[user_id] = []
        AI_LAST_USED[user_id] = now
        history = AI_MEMORY[user_id]

        if rank == "owner":
            system = "You are MOON's AI assistant, talking to the server owner. Answer fully and in detail."
            max_tok = 1024
        elif rank:
            system = f"You are MOON's AI assistant, talking to staff ({rank}). Be detailed and helpful."
            max_tok = 768
        else:
            system = (
                "You are MOON's AI assistant. Only answer questions about server rules, "
                "performance, gameplay, or how to appeal a punishment. Keep answers to 3 sentences or fewer."
            )
            max_tok = 256

        response = await query_ai(system, question, history, max_tok)

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})
        del history[: max(0, len(history) - MAX_HISTORY * 2)]

        embed = discord.Embed(
            title="🌙 MOON AI",
            description=response[:4000],
            color=discord.Color.blurple(),
        )
        await ctx.followup.send(embed=embed)

    # ── /aimodel ─────────────────────────────────────────────────────────────
    @commands.slash_command(name="aimodel", description="View or refresh the active AI model (admin+)")
    @option("action", description="What to do", choices=["status", "refresh", "lock", "unlock"], required=False)
    async def aimodel(self, ctx: discord.ApplicationContext, action: str = "status"):
        if not isinstance(ctx.author, discord.Member) or not can_use(ctx.author, "ban"):
            await ctx.respond("❌ You need at least **Admin** to manage the AI model.", ephemeral=True)
            return

        global AI_MODEL_LOCKED
        await ctx.defer()

        if action == "refresh":
            await select_best_free_model()
        elif action == "lock":
            AI_MODEL_LOCKED = True
        elif action == "unlock":
            AI_MODEL_LOCKED = False

        embed = discord.Embed(title="🌙 MOON AI Model", color=discord.Color.blurple())
        embed.add_field(name="Current model", value=f"`{AI_MODEL}`", inline=False)
        embed.add_field(name="Locked", value=str(AI_MODEL_LOCKED), inline=True)
        embed.add_field(name="Configured", value=str(await is_ai_configured()), inline=True)
        embed.set_footer(text="/aimodel refresh — re-scan free models")
        await ctx.followup.send(embed=embed)

    # ── /moonbrain (owner-only natural language command) ────────────────────
    @commands.slash_command(
        name="moonbrain",
        description="Owner only: describe a moderation action in plain English and MOON will execute it",
    )
    @option("instruction", description="e.g. 'ban Steve123 for duping items'")
    async def moonbrain(self, ctx: discord.ApplicationContext, instruction: str):
        if not isinstance(ctx.author, discord.Member) or get_member_rank(ctx.author) != "owner":
            await ctx.respond("⛔ This command is restricted to the server owner.", ephemeral=True)
            print(f"[MOONBRAIN BLOCKED] user={ctx.author.id} tried: {instruction[:200]}")
            return

        await ctx.defer()

        system = (
            "You are MOON's command engine. The server owner gives a direct instruction. "
            "Respond with ONLY a JSON object, no markdown, no extra text: "
            f"{ACTION_DESCRIPTIONS}"
        )
        raw = await query_ai(system, instruction, None, 400)

        try:
            clean = raw.strip()
            if clean.startswith("```"):
                clean = re.sub(r"^```(?:json)?\n?", "", clean)
                clean = re.sub(r"\n?```$", "", clean)
            parsed = json.loads(clean)
        except Exception:
            await ctx.followup.send(f"⚠️ AI returned invalid JSON:\n```{raw[:500]}```")
            return

        action = (parsed.get("action") or "none").lower()
        player = parsed.get("player")
        reason = parsed.get("reason", "")
        duration = parsed.get("duration_hours")
        message = parsed.get("message", "")

        ok, detail = await self._execute(action, player, reason, duration, message, ctx.author)

        embed = discord.Embed(
            title="🌙 MOON — Owner Command Executed",
            color=discord.Color.green() if ok else discord.Color.red(),
        )
        embed.add_field(name="Instruction", value=instruction[:500], inline=False)
        embed.add_field(name="Parsed action", value=f"`{action}`", inline=True)
        embed.add_field(name="Result", value=detail or "—", inline=False)
        await ctx.followup.send(embed=embed)

    async def _execute(self, action: str, player: str | None, reason: str,
                        duration: int | None, message: str, author: discord.Member) -> tuple[bool, str]:
        """Maps the AI's parsed action onto MOON's existing, already-audited
        punishment/broadcast endpoints — never executes anything outside this
        fixed vocabulary."""
        if action == "none":
            return True, "No action taken."

        if action == "broadcast":
            if not message:
                return False, "No message provided."
            status, resp = await api_post("/api/v1/mc/command", {
                "command": f"say {message}",
                "requested_by_discord_id": str(author.id),
                "requested_by_username": author.display_name,
            })
            return status in (200, 201), f"Broadcast: {message}" if status in (200, 201) else str(resp)

        if not player:
            return False, "No player specified."

        p = await find_player(player)
        if not p:
            return False, f"Player `{player}` not found."

        if action in ("ban", "warn"):
            status, resp = await api_post("/api/v1/punishments", {
                "player_uuid": p["uuid"], "type": action, "reason": reason or "No reason given",
                "issued_by_discord_id": str(author.id),
            })
            return status in (200, 201), f"{action.title()}ned {p['username']}" if status in (200, 201) else str(resp)

        if action == "tempban":
            import datetime
            hours = duration or 24
            status, resp = await api_post("/api/v1/punishments", {
                "player_uuid": p["uuid"], "type": "tempban", "reason": reason or "No reason given",
                "issued_by_discord_id": str(author.id),
                "expires_at": (datetime.datetime.utcnow() + datetime.timedelta(hours=hours)).isoformat() + "Z",
            })
            return status in (200, 201), f"Temp-banned {p['username']} for {hours}h" if status in (200, 201) else str(resp)

        if action == "mute":
            import datetime
            body = {"player_uuid": p["uuid"], "type": "mute", "reason": reason or "No reason given",
                     "issued_by_discord_id": str(author.id)}
            if duration:
                body["expires_at"] = (datetime.datetime.utcnow() + datetime.timedelta(hours=duration)).isoformat() + "Z"
            status, resp = await api_post("/api/v1/punishments", body)
            return status in (200, 201), f"Muted {p['username']}" if status in (200, 201) else str(resp)

        if action == "kick":
            status, resp = await api_post("/api/v1/mc/command", {
                "command": f"kick {p['username']} {reason}",
                "requested_by_discord_id": str(author.id),
                "requested_by_username": author.display_name,
            })
            return status in (200, 201), f"Kicked {p['username']}" if status in (200, 201) else str(resp)

        if action == "unban":
            punishments = await api_get(f"/api/v1/punishments?player_uuid={p['uuid']}&active_only=true")
            ban = next((x for x in (punishments or []) if x.get("type") in ("ban", "tempban")), None)
            if not ban:
                return False, f"{p['username']} is not banned."
            status, resp = await api_post(f"/api/v1/punishments/{ban['id']}/revoke", {})
            return status in (200, 201), f"Unbanned {p['username']}" if status in (200, 201) else str(resp)

        return False, f"Unknown action: {action}"


def setup(bot: discord.Bot):
    bot.add_cog(AIChat(bot))
