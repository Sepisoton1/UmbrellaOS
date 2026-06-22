"""
cogs/fun.py — Harmless fun/utility commands. No permissions required,
no real-world effect on the server. Kept isolated from moderation/AI cogs.
"""
import random
import hashlib

import discord
from discord.ext import commands
from discord import option


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="coinflip", description="Flip a coin")
    async def coinflip(self, ctx: discord.ApplicationContext):
        result = random.choice(["Heads", "Tails"])
        await ctx.respond(f"🪙 **{result}!**")

    @discord.slash_command(name="roll", description="Roll a die")
    @option("sides", description="Number of sides (default 6)", required=False, default=6)
    async def roll(self, ctx: discord.ApplicationContext, sides: int):
        if sides < 2:
            await ctx.respond("Needs at least 2 sides!", ephemeral=True)
            return
        result = random.randint(1, sides)
        await ctx.respond(f"🎲 You rolled a **{result}** (d{sides})")

    @discord.slash_command(name="8ball", description="Ask the magic 8-ball a question")
    @option("question", description="Your question")
    async def eightball(self, ctx: discord.ApplicationContext, question: str):
        answers = [
            "It is certain.", "Without a doubt.", "Yes, definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.",
            "Outlook good.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now.", "Cannot predict now.",
            "Don't count on it.", "My reply is no.",
            "My sources say no.", "Outlook not so good.", "Very doubtful.",
        ]
        await ctx.respond(f"🎱 **{question}**\n> {random.choice(answers)}")

    @discord.slash_command(name="rps", description="Rock, paper, scissors vs the bot")
    @option("choice", description="Your move", choices=["rock", "paper", "scissors"])
    async def rps(self, ctx: discord.ApplicationContext, choice: str):
        bot_choice = random.choice(["rock", "paper", "scissors"])
        beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if choice == bot_choice:
            outcome = "It's a tie!"
        elif beats[choice] == bot_choice:
            outcome = "You win!"
        else:
            outcome = "I win!"
        emoji = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        await ctx.respond(
            f"{emoji[choice]} vs {emoji[bot_choice]} — **{outcome}**"
        )

    @discord.slash_command(name="ship", description="Calculate compatibility between two people")
    @option("person1", description="First person")
    @option("person2", description="Second person")
    async def ship(
        self,
        ctx: discord.ApplicationContext,
        person1: discord.Member,
        person2: discord.Member,
    ):
        # Deterministic "random" % so the same pair always gets the same score
        seed = "-".join(sorted([str(person1.id), str(person2.id)]))
        pct = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % 101

        if pct >= 90:
            verdict = "💞 Soulmates!"
        elif pct >= 70:
            verdict = "💕 Great match!"
        elif pct >= 40:
            verdict = "🤝 Could work!"
        elif pct >= 15:
            verdict = "😐 Rocky..."
        else:
            verdict = "💀 Run."

        bar_filled = "█" * (pct // 10)
        bar_empty = "░" * (10 - pct // 10)
        await ctx.respond(
            f"💘 **{person1.display_name}** + **{person2.display_name}**\n"
            f"`{bar_filled}{bar_empty}` **{pct}%**\n{verdict}"
        )

    @discord.slash_command(name="poll", description="Create a quick yes/no style poll")
    @option("question", description="The poll question")
    @option("option1", description="First option")
    @option("option2", description="Second option")
    async def poll(
        self,
        ctx: discord.ApplicationContext,
        question: str,
        option1: str,
        option2: str,
    ):
        embed = discord.Embed(title="📊 " + question, color=discord.Color.blurple())
        embed.add_field(name="1️⃣", value=option1, inline=True)
        embed.add_field(name="2️⃣", value=option2, inline=True)
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")
        await ctx.respond(embed=embed)
        msg = await ctx.interaction.original_response()
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")


def setup(bot):
    bot.add_cog(Fun(bot))
