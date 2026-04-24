import discord
from discord import app_commands
from discord.ext import commands
import json
from config import settings
from model.dbc_model import Tournament_DB
from model.dbc_model import Teams
from common.ollama_seeding import generate_bracket_with_ai
from common.tournament_runner import TournamentRunner

logger = settings.logging.getLogger("discord")


class Seeding(commands.Cog):
    """Cog for tournament seeding commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # /seed_demo
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

    # /seed_real
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

    # /seed_from_matchmaking
    @app_commands.command(
        name="seed_from_matchmaking",
        description="Generate bracket using latest matchmaking results"
    )
    async def seed_from_matchmaking(self, interaction: discord.Interaction):

        db = Tournament_DB()

        try:
            try:
                await interaction.response.defer(thinking=True)
            except:
                pass

            logger.info("[DEBUG] Starting seed_from_matchmaking")

            #Get latest matchmaking session
            db.cursor.execute("""
                SELECT DISTINCT matchmaking_session
                FROM Matches
                WHERE matchmaking_session IS NOT NULL
                ORDER BY match_num DESC
                LIMIT 1
            """)

            result = db.cursor.fetchone()
            logger.info(f"[DEBUG] Session query result: {result}")

            if not result:
                await interaction.followup.send("No matchmaking session found.")
                return

            session_id = result[0]
            logger.info(f"[DEBUG] Using session: {session_id}")

            #Get teams from most recent session
            db.cursor.execute("""
                SELECT m.teamId, m.teamUp, p.player_name
                FROM Matches m
                JOIN player p ON m.user_id = p.user_id
                WHERE m.matchmaking_session = ?
                AND m.teamUp IN ('team1','team2')
                ORDER BY m.match_num, m.teamUp
            """, (session_id,))

            rows = db.cursor.fetchall()
            logger.info(f"[DEBUG] Rows fetched: {len(rows)}")
            logger.debug(f"[DEBUG] Raw rows: {rows}")

            if not rows:
                await interaction.followup.send("No matchmaking data found.")
                return

            #build teams
            teams = {}

            for team_id, team_up, player_name in rows:
                key = f"{team_id}_{team_up}"

                if key not in teams:
                    teams[key] = {
                        "team_name": key,
                        "players": []
                    }

                if player_name and player_name not in teams[key]["players"]:
                    teams[key]["players"].append(player_name)

            logger.info(f"[DEBUG] Teams dict built: {len(teams)} teams")
            logger.debug(f"[DEBUG] Teams dict: {teams}")

            ai_teams = [t for t in teams.values() if t["players"]]

            logger.info(f"[DEBUG] Filtered ai_teams count: {len(ai_teams)}")
            logger.debug(f"[DEBUG] ai_teams: {ai_teams}")

            if len(ai_teams) < 2:
                await interaction.followup.send("Not enough teams to generate bracket.")
                return

            logger.info("[DEBUG] Calling generate_bracket_with_ai")

            bracket = generate_bracket_with_ai(ai_teams)

            logger.info(f"[DEBUG] Raw bracket response: {bracket}")

            if not bracket:
                await interaction.followup.send("⚠️ Failed to generate bracket.")
                return

            if "error" in bracket:
                logger.error(f"[DEBUG] Bracket error: {bracket}")
                await interaction.followup.send("⚠️ Error generating bracket.")
                return

            if "matches" not in bracket:
                logger.error(f"[DEBUG] Missing 'matches' key in bracket: {bracket}")
                await interaction.followup.send("⚠️ Invalid bracket structure.")
                return

            if not bracket["matches"]:
                logger.error("[DEBUG] Bracket returned empty matches list.")
                await interaction.followup.send("⚠️ No matches were generated.")
                return

            logger.info(f"[DEBUG] Final match count: {len(bracket['matches'])}")

            runner = TournamentRunner(interaction, bracket["matches"])
            await runner.start()

        except Exception as e:
            logger.exception(f"[DEBUG] Seed from matchmaking crashed: {e}")

            try:
                await interaction.followup.send(f"❌ ERROR:\n```{str(e)}```")
            except:
                pass

        finally:
            db.close_db()

    #/start_tournament
    @app_commands.command(
        name="start_tournament",
        description="Start a tournament with interactive bracket UI"
    )
    async def start_tournament(self, interaction: discord.Interaction):

        try:
            await interaction.response.defer()

            teams_db = Teams()
            teams = teams_db.get_all_teams_with_members()

            if not teams or len(teams) < 2:
                await interaction.followup.send("Need at least 2 teams.")
                return

            bracket = generate_bracket_with_ai(teams)

            if "error" in bracket:
                await interaction.followup.send(
                    f"⚠️ AI error:\n```{bracket['raw'][:1500]}```"
                )
                return

            runner = TournamentRunner(interaction, bracket["matches"])
            await runner.start()

        except Exception as e:
            logger.error(f"Tournament start error: {e}")
            await interaction.followup.send("Error starting tournament.")


#Setup
async def setup(bot: commands.Bot):
    await bot.add_cog(Seeding(bot))