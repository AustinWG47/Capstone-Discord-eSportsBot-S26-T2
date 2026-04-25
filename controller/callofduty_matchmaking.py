import discord
import asyncio
import random
import json
import sqlite3
from discord import app_commands
from discord.ext import commands
from config import settings
from model.dbc_model import Tournament_DB, Game



#Random player insertion for testing and demo
db = Tournament_DB()

def insert_test_players():
    players = []

    for i in range(1, 25):
        user_id = 1000 + i  # simple unique IDs

        player_name = f"TestPlayer{i}"
        tag_id = f"#{1000 + i}"

        wins = random.randint(0, 20)
        losses = random.randint(0, 20)

        # prevent division by zero (for WR column)
        if wins + losses == 0:
            losses = 1

        kda = round(random.uniform(0.3, 5.0), 2)

        players.append((
            user_id,
            "Call Of Duty",
            player_name,
            tag_id,
            wins,
            losses,
            kda
        ))

        db.cursor.execute("""
            INSERT INTO player
            (user_id, game_name, player_name, tag_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, "Call Of Duty", player_name, tag_id))

    db.cursor.executemany("""
        INSERT INTO cod_game_details
        (user_id, game_name, player_name, tag_id, wins, losses, kda)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, players)

    db.connection.commit()
    db.close_db()

#real matchamking below

logger = settings.logging.getLogger("discord")

class CODMatchmakingController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="insert_codtest_players", description="Insert test players into the database")
    async def insert_test_players_command(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            try:
                insert_test_players()
                await interaction.response.send_message("Test players inserted successfully!", ephemeral=True)
            except Exception as ex:
                await interaction.response.send_message(f"Error inserting test players: {ex}", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)

    @app_commands.command(name="run_cod_matchmaking", description="Run Call of Duty matchmaking with registered players")
    @app_commands.describe(
        players_per_game="Number of players per game (default: 12)",
        selection_method="How to select players who sit out: (default: random)"
    )
    async def cod_run_matchmaking(
            self,
            interaction: discord.Interaction,
            players_per_game: int = 12,
            selection_method: str = "random"
    ):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.defer(thinking=True)

            try:
                # Get all eligible players
                db = Tournament_DB()
                
                all_players = []

                import uuid
                session_id = f"session_{uuid.uuid4().hex[:8]}"

                try:
                    # Get all players with game data
                    db.cursor.execute("""
                        SELECT p.user_id,p.player_name, p.game_name, p.tag_id, g.wins, g.losses, g.wr, g.kda
                        FROM player p
                        JOIN cod_game_details g ON p.user_id = g.user_id
                        GROUP BY p.user_id
                        ORDER BY g.KDA DESC
                    """)

                    player_records = db.cursor.fetchall()

                    for record in player_records:
                        user_id, player_name, game_name, tag_id, wins, losses, wr, KDA = record

                        player = {
                            'user_id': user_id,
                            'player_name': player_name,
                            'game_name': game_name,
                            'tag_id': tag_id,
                            'wins': wins if wins is not None else 0,
                            'losses': losses if losses is not None else 0,
                            'wr': float(wr) if wr is not None else 50.0,
                            'kda': float(KDA) if KDA is not None else 1.0,
                        }

                        all_players.append(player)

                except Exception as ex:
                    logger.error(f"Error fetching players: {ex}")
                    await interaction.followup.send(f"Error fetching players: {str(ex)}")
                    return

                # Calculate how many games we can run and if we need players to sit out
                total_players = len(all_players)

                if total_players < players_per_game:
                    await interaction.followup.send(
                        f"Not enough players for matchmaking. Need at least {players_per_game} players, but only have {total_players}."
                    )
                    return

                game_count = total_players // players_per_game
                extra_players = total_players % players_per_game

                await interaction.followup.send(
                    f"Found {total_players} registered players.\n"
                    f"Can create {game_count} games with {players_per_game} players each.\n"
                    f"{extra_players} players will sit out and receive participation points."
                )

                # If we have extra players, determine who sits out
                players_to_exclude = []
                participation_players = []

                if extra_players > 0:
                    selection_method = selection_method.lower()

                    # Default to random
                    # Randomly select players to sit out
                    random_players = random.sample(all_players, extra_players)
                    for player in random_players:
                        players_to_exclude.append(player['player_name'])
                        participation_players.append(player)

                    await interaction.followup.send(                          
                        f"**Using random selection:** {extra_players} randomly selected players will sit out but receive participation points."
                        )

                # Remove excluded players
                filtered_players = [p for p in all_players if p['player_name'] not in players_to_exclude]

                # Split players into pools based on skill
                filtered_players.sort(key=lambda p: p.get('kda', 0), reverse=True)

                # Create pools for skill-based games
                pools = []
                for i in range(game_count):
                    start_idx = i * players_per_game
                    end_idx = start_idx + players_per_game
                    pool = filtered_players[start_idx:end_idx]
                    pools.append(pool)

                # Run matchmaking for each pool
                results = []

                for pool_idx, pool in enumerate(pools):
                    # Get the next match ID
                    from model.dbc_model import Matches
                    matches_db = Matches(db_name=settings.DATABASE_NAME)
                    match_num = matches_db.get_next_match_id()
                    match_id = f"match_{match_num}"

                    # Split pool into balanced teams
                    team1, team2 = [], []
                    team1_kda = 0
                    team2_kda = 0

                    # assign to pools
                    for player in pool:
                        kda = player.get('kda', 0)

                        if team1_kda <= team2_kda:
                            team1.append(player)
                            team1_kda += kda
                        else:
                            team2.append(player)
                            team2_kda += kda

                    # Record match in database
                    for player in team1:
                        user_id = player.get('user_id')
                        if user_id:
                            query = "INSERT INTO Matches(user_id, teamUp, teamId, match_num, game_name, matchmaking_session) VALUES(?, ?, ?, ?, ?, ?)"
                            db.cursor.execute(query, (user_id, "team1", match_id, match_num, "Call Of Duty", session_id))

                    for player in team2:
                        user_id = player.get('user_id')
                        if user_id:
                            query = "INSERT INTO Matches(user_id, teamUp, teamId, match_num, game_name, matchmaking_session) VALUES(?, ?, ?, ?, ?, ?)"
                            db.cursor.execute(query, (user_id, "team2", match_id, match_num, "Call Of Duty", session_id))


                    # Create embeds for the teams
                    team1_embed = discord.Embed(
                        title=f"Game {pool_idx + 1} - Team 1 (Match ID: {match_id})",
                        color=discord.Color.blue(),
                        description=f"Game {pool_idx + 1} of {game_count}\nOverall K/D: {team1_kda/6:.2f}"
                    )

                    team2_embed = discord.Embed(
                        title=f"Game {pool_idx + 1} - Team 2 (Match ID: {match_id})",
                        color=discord.Color.red(),
                        description=f"Game {pool_idx + 1} of {game_count}\nOverall K/D: {team2_kda/6:.2f}"
                    )
                    
                    # Add players to embeds
                    for i, player in enumerate(team1):
                        name = player.get('player_name', player.get('user_id', 'Unknown'))
                        wr = f"{player.get('wr', 0):.1f}%"
                        kda = f"{player.get('kda', 0):.2f}"
                        
                        team1_embed.add_field(
                            name=f"Player {i + 1}: {name}",
                            value=f"**WR:** {wr}\n**KDA:** {kda}",
                            inline=True
                        )

                    for i, player in enumerate(team2):
                        name = player.get('player_name', player.get('user_id', 'Unknown'))
                        wr = f"{player.get('wr', 0):.1f}%"
                        kda = f"{player.get('kda', 0):.2f}"
                        
                        team2_embed.add_field(
                            name=f"Player {i + 1}: {name}",
                            value=f"**WR:** {wr}\n**KDA:** {kda}",
                            inline=True
                        )
                    
                    # Instructions for recording match outcome
                    instructions = (
                        f"**Call Of Duty Matchmaking - Game {pool_idx + 1} of {game_count}**\nTeam 1 K/D: {team1_kda/6:.2f} | Team 2 K/D: {team2_kda/6:.2f}\n"
                        f"Match ID: `{match_id}`\n"
                        f"To record match results, use: `/record_match_result {match_id} <winning_team>`\n"
                        f"where <winning_team> is either 1 or 2."
                    )

                    results.append({
                        "match_id": match_id,
                        "pool_idx": pool_idx,
                        "embeds": [team1_embed, team2_embed],
                        "instructions": instructions
                    })

                # Record participation points for excluded players
                if participation_players:
                    participation_id = f"participation_{int(asyncio.get_event_loop().time())}"
                    # Get the next match ID for the participation session
                    from model.dbc_model import Matches
                    matches_db = Matches(db_name=settings.DATABASE_NAME)
                    participation_match_num = matches_db.get_next_match_id()
                    for player in participation_players:
                        user_id = player.get('user_id')
                        if user_id:
                            query = "INSERT INTO Matches(user_id, teamUp, teamId, match_num, game_name, matchmaking_session) VALUES(?, ?, ?, ?, ?, ?)"
                            db.cursor.execute(query, (user_id, "participation", participation_id, participation_match_num, "Call Of Duty", session_id))

                # Commit all changes to database
                db.connection.commit()
                db.close_db()

                # Send results for each game
                for result in results:
                    await interaction.followup.send(content=result["instructions"], embeds=result["embeds"])

                # If there were participation players, show them too
                if participation_players:
                    participation_embed = discord.Embed(
                        title="Players Receiving Participation Points",
                        color=discord.Color.green(),
                        description=f"{len(participation_players)} players are sitting out but will receive participation points."
                    )

                    for i, player in enumerate(participation_players):
                        name = player.get('player_name', player.get('user_id', 'Unknown'))
                        wr = player.get('wr', '')
                        kda = player.get('kda', '')

                        participation_embed.add_field(
                            name=f"Player {i + 1}: {name}",
                            value=f"**WR:** {wr}\n**KDA:** {kda}",
                            inline=True
                        )

                    await interaction.followup.send(embed=participation_embed)

            except Exception as ex:
                logger.error(f"Error running matchmaking: {ex}")
                await interaction.followup.send(f"Error running matchmaking: {str(ex)}")
        else:
            await interaction.response.send_message("Sorry, you don't have required permission to use this command",
                                                  ephemeral=True)

async def setup(bot):
    await bot.add_cog(CODMatchmakingController(bot))