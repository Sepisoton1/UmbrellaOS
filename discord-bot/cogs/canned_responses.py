"""
cogs/canned_responses.py — Exact-match text triggers, configured from
the dashboard instead of hardcoded.

Currently:
  !ip  -> replies with Settings -> discord.ip_response
"""
import discord
from discord.ext import commands
from settings_client import get_setting


class CannedResponses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.content.strip().lower() == "!ip":
            ip_response = await get_setting("discord.ip_response")
            if not ip_response:
                await message.channel.send(
                    "⚠️ Server IP isn't set yet — set it in Dashboard → Settings → Discord."
                )
                return
            await message.channel.send(ip_response)


def setup(bot):
    bot.add_cog(CannedResponses(bot))
