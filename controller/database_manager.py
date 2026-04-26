import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from model.dbc_model import Tournament_DB

class DatabaseManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="clear_db",
        description="Delete ALL data from the DB (admin only)"
    )
    async def clear_matches(self, interaction: discord.Interaction):
        # Permission check
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You don't have permission to use this command.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:

            # Run blocking SQLite safely off the event loop
            def clear_tables():
                db = Tournament_DB()
                db.cursor.execute("DELETE FROM Matches;")
                db.cursor.execute("DELETE FROM cod_game_details;")
                db.cursor.execute("DELETE FROM mr_game_details;")
                db.cursor.execute("DELETE FROM league_game_details;")
                db.cursor.execute("DELETE FROM Counters;")
                db.cursor.execute("DELETE FROM player;")
                db.cursor.execute("DELETE FROM playerGameDetail;")
                db.cursor.execute("DELETE FROM MVP_Votes;")
                db.cursor.execute("DELETE FROM teams;")
                db.cursor.execute("DELETE FROM team_members;")     
                db.cursor.execute("INSERT INTO Counters(name, value) VALUES ('match_counter', 0);")
                db.connection.commit()
                db.close_db()

            await asyncio.to_thread(clear_tables)

            await interaction.followup.send(
                "All data from DB table has been removed successfully.",
                ephemeral=True
            )

        except Exception as ex:
            await interaction.followup.send(
                f"Error clearing Matches table: {ex}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(DatabaseManager(bot))