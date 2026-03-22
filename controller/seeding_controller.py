import discord
from discord import app_commands
from discord.ext import commands
import json
from config import settings

from model.dbc_model import Teams
from ollama_seeding import generate_bracket_with_ai

logger = settings.logging.getLogger("discord")


class Seeding(commands.Cog):
    """Cog for tournament seeding commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------
    # /seed_demo (SAFE FALLBACK)
    # -------------------------------
    @app_commands.command(
        name="seed_demo",
        description="Generate demo tournament brackets with AI"
    )
    async def seed_demo(self, interaction: discord.Interaction):

        demo_teams = [
            {"team_name": "Thrashers", "players": ["Alice", "Bob", "Charlie", "David", "Eve"]},
            {"team_name": "Crashers", "players": ["Frank", "Grace", "Hannah", "Isaac", "Jack"]},
            {"team_name": "Trashers", "players": ["Karen", "Leo", "Mia", "Nina", "Owen"]},
            {"team_name": "Bashers", "players": ["Paul", "Quinn", "Rita", "Steve", "Tina"]}
        ]

        try:
            await interaction.response.defer()

            bracket = generate_bracket_with_ai(demo_teams)

            if "error" in bracket:
                await interaction.followup.send(
                    f"⚠️ AI returned invalid JSON:\n```{bracket['raw'][:1500]}```"
                )
                return

            await interaction.followup.send(
                f"```json\n{json.dumps(bracket, indent=2)}\n```"
            )

        except Exception as e:
            logger.error(f"Seeding demo error: {e}")
            await interaction.followup.send("Error generating demo bracket.")

    # -------------------------------
    # /seed_real (DB INTEGRATION)
    # -------------------------------
    @app_commands.command(
        name="seed_real",
        description="Generate tournament bracket using real DB teams"
    )
    async def seed_real(self, interaction: discord.Interaction):

        try:
            await interaction.response.defer()

            teams_db = Teams()
            teams = teams_db.get_all_teams_with_members()

            if not teams:
                await interaction.followup.send("No teams found in database.")
                return

            if len(teams) < 2:
                await interaction.followup.send("Need at least 2 teams.")
                return

            bracket = generate_bracket_with_ai(teams)

            if "error" in bracket:
                await interaction.followup.send(
                    f"⚠️ AI returned invalid JSON:\n```{bracket['raw'][:1500]}```"
                )
                return

            await interaction.followup.send(
                f"```json\n{json.dumps(bracket, indent=2)}\n```"
            )

        except Exception as e:
            logger.error(f"Seeding real error: {e}")
            await interaction.followup.send("Error generating real bracket.")


# -------------------------------
# Setup
# -------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(Seeding(bot))

