"""
cogs/verification.py — Discord bot verification cog.

Handles DM-based player verification for cracked Minecraft servers,
plus an owner-gated /verify and /unlink command to manually link a
Discord account to a Minecraft username. Access is controlled by the
same can_manual_verify() allowlist used in moderation.py — owner by
default, plus anyone granted access via /grant-verify.
"""
import httpx
import discord
from discord.ext import commands
from config import config
from cogs.moderation import can_manual_verify


class Verification(commands.Cog):
    """Verification cog for Discord-based player verification."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle DM messages for verification codes."""
        if message.guild is not None:
            return

        if message.author.bot:
            return

        content = message.content.strip()
        if not content.isdigit() or len(content) != 6:
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.UMBRELLA_API_URL}/api/v1/verification/confirm",
                    headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
                    json={
                        "discord_id": str(message.author.id),
                        "discord_username": message.author.name,
                        "code": content,
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    await message.reply("✅ Verified! You can now play on the server.")
                elif response.status_code == 404:
                    await message.reply("❌ Invalid code. Please check and try again.")
                elif response.status_code == 400:
                    detail = response.json().get("detail", "")
                    if "expired" in detail.lower():
                        await message.reply("❌ Code expired. Rejoin the server for a new code.")
                    elif "used" in detail.lower():
                        await message.reply("✅ Already verified!")
                    else:
                        await message.reply("❌ Invalid code. Please check and try again.")
                else:
                    await message.reply("⚠️ Something went wrong. Please try again.")

        except Exception as e:
            print(f"[Verification] Error confirming code: {e}")
            await message.reply("⚠️ Something went wrong. Please try again.")

    @commands.slash_command(name="verify", description="Link a Discord account to a Minecraft username")
    async def verify(
        self,
        ctx: discord.ApplicationContext,
        discord_user: discord.Member = discord.Option(
            discord.Member,
            description="Discord account to link",
        ),
        minecraft_username: str = discord.Option(
            str,
            description="Minecraft username to link",
        ),
    ):
        """Manually link a Discord user to a Minecraft username.
        Owner-only by default — grant access via /grant-verify."""
        if not can_manual_verify(ctx.author):
            await ctx.respond("❌ You don't have permission to use this command.", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.UMBRELLA_API_URL}/api/v1/verification/manual-link",
                    headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
                    json={
                        "discord_id": str(discord_user.id),
                        "mc_username": minecraft_username,
                    },
                    timeout=5.0,
                )

                if response.status_code == 200:
                    await ctx.respond(
                        f"✅ Linked **{discord_user.display_name}** to `{minecraft_username}`. "
                        "UUID will resolve automatically next time they join.",
                        ephemeral=True,
                    )
                else:
                    detail = response.json().get("detail", response.status_code)
                    await ctx.respond(f"❌ Backend error: {detail}", ephemeral=True)

        except Exception as e:
            print(f"[Verification] Error linking: {e}")
            await ctx.respond("⚠️ Something went wrong. Please try again.", ephemeral=True)

    @commands.slash_command(name="unlink", description="Remove a Discord-Minecraft account link")
    async def unlink(
        self,
        ctx: discord.ApplicationContext,
        discord_user: discord.Member = discord.Option(
            discord.Member,
            description="Discord account to unlink",
        ),
    ):
        """Remove an existing Discord<->Minecraft link.
        Owner-only by default — grant access via /grant-verify."""
        if not can_manual_verify(ctx.author):
            await ctx.respond("❌ You don't have permission to use this command.", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{config.UMBRELLA_API_URL}/api/v1/verification/unlink/{discord_user.id}",
                    headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
                    timeout=5.0,
                )

                if response.status_code == 200:
                    await ctx.respond(f"✅ Unlinked **{discord_user.display_name}**.", ephemeral=True)
                elif response.status_code == 404:
                    await ctx.respond(f"❌ **{discord_user.display_name}** isn't linked to anything.", ephemeral=True)
                else:
                    detail = response.json().get("detail", response.status_code)
                    await ctx.respond(f"❌ Backend error: {detail}", ephemeral=True)

        except Exception as e:
            print(f"[Verification] Error unlinking: {e}")
            await ctx.respond("⚠️ Something went wrong. Please try again.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Verification(bot))
