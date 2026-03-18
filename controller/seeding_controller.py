import discord
from discord import app_commands
from discord.ext import commands
import random
import json
from config import settings
import logging

logger = settings.logging.getLogger("discord")


class Seeding(commands.Cog):
    """Cog for tournament seeding commands using AI (demo bracket)"""

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
            {"team_name": "Bashers", "players": ["Karen", "Leo", "Mia", "Nina", "Owen"]},
            {"team_name": "Trashers", "players": ["Paul", "Quinn", "Rita", "Steve", "Tina"]}
        ]

        try:
            # Defer the response to avoid timeout
            await interaction.response.defer()

            # Randomize bracket order
            random.shuffle(demo_teams)

            # Pair teams into matchups
            matchups = []
            for i in range(0, len(demo_teams), 2):
                if i + 1 < len(demo_teams):
                    matchups.append({
                        "match": f"{demo_teams[i]['team_name']} vs {demo_teams[i+1]['team_name']}",
                        "teams": [demo_teams[i], demo_teams[i+1]]
                    })
                else:
                    # Odd number of teams -> last team gets a bye
                    matchups.append({
                        "match": f"{demo_teams[i]['team_name']} has a bye",
                        "teams": [demo_teams[i]]
                    })

            # Send the formatted bracket
            await interaction.followup.send(
                f"```json\n{json.dumps(matchups, indent=2)}\n```"
            )

        except Exception as e:
            logger.error(f"Seeding error: {e}")
            await interaction.followup.send(
                "❌ Error generating teams. Check logs."
            )


# -------------------------------
# Required setup function
# -------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(Seeding(bot))
