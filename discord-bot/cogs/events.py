"""
cogs/events.py — Discord bot events cog.

Polls for Minecraft bridge messages and forwards chat + lifecycle events to Discord.
"""
import httpx
import discord
from discord.ext import commands, tasks
from config import config

EVENT_KEYWORDS = (
    "joined the server",
    "left the server",
    "died",
    "earned",
    "achievement",
    "server is online",
    "server is shutting down",
)


class Events(commands.Cog):
    """Poll Minecraft bridge messages and forward to Discord."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.bridge_channel_id = config.BRIDGE_CHANNEL_ID
        self.last_seen_id = 0

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.poll_bridge_messages.is_running():
            self.poll_bridge_messages.start()
        print("[Events] Bridge polling started")

    def cog_unload(self):
        self.poll_bridge_messages.cancel()

    def _is_lifecycle_event(self, message: str) -> bool:
        lower = message.lower()
        return any(keyword in lower for keyword in EVENT_KEYWORDS)

    async def _format_event(self, player_name: str, message: str) -> str | None:
        lower = message.lower()
        if "joined the server" in lower:
            return f"🟢 **{player_name}** joined the server"
        if "left the server" in lower:
            return f"🔴 **{player_name}** left the server"
        if "died" in lower:
            return f"💀 **{player_name}** died: {message}"
        if "earned" in lower or "achievement" in lower:
            return f"🏆 **{player_name}** earned: {message}"
        if "server is online" in lower:
            return "🟢 Server is online"
        if "server is shutting down" in lower:
            return "🔴 Server is shutting down"
        return None

    @tasks.loop(seconds=5)
    async def poll_bridge_messages(self):
        """Single poll loop for chat and lifecycle events."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{config.UMBRELLA_API_URL}/api/v1/bridge/messages?source=minecraft&limit=50",
                    headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
                    timeout=5.0,
                )
                if response.status_code != 200:
                    return

                for msg in response.json():
                    msg_id = msg.get("id", 0)
                    if msg_id <= self.last_seen_id:
                        continue
                    self.last_seen_id = msg_id

                    text = msg.get("message", "")
                    player_name = msg.get("player_name") or msg.get("player_uuid", "Unknown")

                    if self._is_lifecycle_event(text):
                        formatted = await self._format_event(player_name, text)
                        if formatted:
                            channel = self.bot.get_channel(self.bridge_channel_id)
                            if channel:
                                await channel.send(formatted)
                        continue

                    chat_bridge = self.bot.get_cog("ChatBridge")
                    if chat_bridge:
                        await chat_bridge.send_to_discord(player_name, text, "minecraft")
        except Exception as e:
            print(f"[Events] Error polling bridge messages: {e}")

    @poll_bridge_messages.before_loop
    async def before_poll(self):
        await self.bot.wait_until_ready()


def setup(bot: discord.Bot):
    bot.add_cog(Events(bot))
