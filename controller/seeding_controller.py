import discord
from discord import app_commands
from discord.ext import commands
import json
import random
from config import settings
import logging

logger = settings.logging.getLogger("discord")

class Seeding(commands.Cog):
    """Cog for tournament seeding commands (demo teams)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------
    # Slash command: /seed_demo
    # -------------------------------
    @app_commands.command(
        name="seed_demo",
        description="Generate demo tournament brackets with randomized teams"
    )
    async def seed_demo(self, interaction: discord.Interaction):
        # Demo teams for presentation
        demo_teams = [
            {"team_name": "Thrashers", "players": ["Alice", "Bob", "Charlie", "David", "Eve"]},
            {"team_name": "Crashers", "players": ["Frank", "Grace", "Hannah", "Isaac", "Jack"]},
            {"team_name": "Trashers", "players": ["Karen", "Leo", "Mia", "Nina", "Owen"]},
            {"team_name": "Bashers", "players": ["Paul", "Quinn", "Rita", "Steve", "Tina"]}
        ]

        try:
            # Defer response to avoid timeout
            await interaction.response.defer()

            # Randomize the bracket
            random.shuffle(demo_teams)

            # Send formatted JSON
            await interaction.followup.send(
                f"```json\n{json.dumps(demo_teams, indent=2)}\n```"
            )

        except Exception as e:
            logger.error(f"Seeding error: {e}")
            await interaction.followup.send("❌ Error generating demo teams. Check logs.")

# -------------------------------
# Required setup function
# -------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(Seeding(bot))
