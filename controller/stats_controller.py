import discord
from discord import app_commands
from discord.ext import commands

from model.dbc_model import Tournament_DB, Player, Game

class StatsController(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stats", description="View detailed player stats and rank (from database).")
    @app_commands.describe(user="Optional: select a user to view stats for")
    async def stats(self, interaction: discord.Interaction, user: discord.Member | None = None):
        target = user or interaction.user
        user_id = target.id

        # Ensure DB + tables exist
        db = Tournament_DB()
        Player.createTable(db)
        Game.createTable(db)

        # Pull latest stats from Game table
        db.cursor.execute(
            "SELECT player_name,game_name, tier, rank, wins, losses, wr, game_date "
            "FROM league_game_details WHERE user_id = ? "
            "ORDER BY game_date DESC LIMIT 1",
            (user_id,)
        )
        row = db.cursor.fetchone()

        if not row:
            await interaction.response.send_message(
                f"No stats found for {target.display_name}. They may not be registered yet.",
                ephemeral=True
            )
            return

        game_name, tier, rank, wins, losses, wr, game_date = row

        # Simple embed output
        embed = discord.Embed(title=f"Stats for {target.display_name}")
        embed.add_field(name="Game", value=str(game_name), inline=False)
        embed.add_field(name="Rank", value=f"{tier} {rank}", inline=True)
        embed.add_field(name="Wins / Losses", value=f"{wins} / {losses}", inline=True)
        embed.add_field(name="Win Rate", value=str(wr), inline=True)
        embed.set_footer(text=f"Last updated: {game_date}")

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatsController(bot))