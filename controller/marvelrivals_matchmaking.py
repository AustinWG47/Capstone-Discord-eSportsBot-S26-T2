import discord
import asyncio
import random
import json
import sqlite3
from discord import app_commands
from discord.ext import commands
from config import settings
from model.dbc_model import Tournament_DB



#Random player insertion for testing and demo
db = Tournament_DB()

def insert_test_players():
    players = []

    for i in range(1, 25):
        user_id = 2000 + i  # simple unique IDs

        player_name = f"TestPlayer{i}"
        tag_id = f"#{1000 + i}"

        wins = random.randint(0, 20)
        losses = random.randint(0, 20)
        tier = random.choice(["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Grandmaster", "Celestial", "Eternity", "One Above All"])
        if tier in ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Grandmaster", "Celestial"]:
            rank = random.choice(["1", "2", "3"])
        else:
            rank = "1"

        # prevent division by zero (for WR column)
        if wins + losses == 0:
            losses = 1

        kda = round(random.uniform(0.3, 5.0), 2)

        players.append((
            user_id,
            "Marvel Rivals",
            player_name,
            tag_id,
            rank,
            tier,
            wins,
            losses,
            kda
        ))

        db.cursor.execute("""
            INSERT INTO player
            (user_id, game_name, player_name, tag_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, "Marvel Rivals", player_name, tag_id))

    db.cursor.executemany("""
        INSERT INTO mr_game_details
        (user_id, game_name, player_name, tag_id, rank, tier, wins, losses, kda)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, players)

    db.connection.commit()
    db.close_db()

#real matchamking below

logger = settings.logging.getLogger("discord")

class MarvelRivalsMatchmakingController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="insert_marvelrivals_test_players", description="Insert test players into the database")
    async def insert_test_players_command(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            try:
                insert_test_players()
                await interaction.response.send_message("Test players inserted successfully!", ephemeral=True)
            except Exception as ex:
                await interaction.response.send_message(f"Error inserting test players: {ex}", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)

    @app_commands.command(name="run_marvelrivals_matchmaking", description="Run Marvel Rivals matchmaking with registered players")
    @app_commands.describe(
        players_per_game="Number of players per game (default: 12)",
        selection_method="How to select players who sit out: (default: random)"
    )
    async def marvelrivals_run_matchmaking(
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
                        SELECT p.user_id,p.player_name, p.game_name, p.tag_id, g.wins, g.losses, g.wr, g.kda, g.tier, g.rank
                        FROM player p
                        JOIN mr_game_details g ON p.user_id = g.user_id
                    """)

                    player_records = db.cursor.fetchall()

                    for record in player_records:
                        user_id, player_name, game_name, tag_id, wins, losses, wr, kda, tier, rank = record

                        player = {
                            'user_id': user_id,
                            'player_name': player_name,
                            'game_name': game_name,
                            'tag_id': tag_id,
                            'wins': wins if wins is not None else 0,
                            'losses': losses if losses is not None else 0,
                            'wr': float(wr) if wr is not None else 50.0,
                            'tier': tier if tier is not None else "Unranked",
                            'rank': rank if rank is not None else "0",
                            'kda': float(kda) if kda is not None else 1.0,
                            'rank_value': 0  # will be calculated later
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

                RANK_VALUES = {
                    "Bronze 3": 1, "Bronze 2": 2, "Bronze 1": 3,
                    "Silver 3": 4, "Silver 2": 5, "Silver 1": 6,
                    "Gold 3": 7, "Gold 2": 8, "Gold 1": 9,
                    "Platinum 3": 10, "Platinum 2": 11, "Platinum 1": 12,
                    "Diamond 3": 13, "Diamond 2": 14, "Diamond 1": 15,
                    "Grandmaster 3": 16, "Grandmaster 2": 17, "Grandmaster 1": 18,
                    "Celestial 3": 19, "Celestial 2": 20, "Celestial 1": 21,
                    "Eternity 1": 30, "One Above All 1": 40,
                }

                for player in filtered_players:
                    rank_key = f"{player['tier']} {player['rank']}"
                    player["rank_value"] = RANK_VALUES.get(rank_key, 0)

                pools = []
                for i in range(game_count):
                    start_idx = i * players_per_game
                    end_idx = start_idx + players_per_game
                    pool = filtered_players[start_idx:end_idx]
                    pools.append(pool)

                # Run matchmaking for each pool
                results = []


                from model.dbc_model import Matches
                matches_db = Matches(db_name=settings.DATABASE_NAME)
                base_match_num = matches_db.get_next_match_id()

                for pool_idx, pool in enumerate(pools):
                    #sort by skill within pool
                    pool.sort(key=lambda p: p["rank_value"], reverse=True)
                    # Get the next match ID
                    match_num = base_match_num + pool_idx
                    match_id = f"match_{match_num}"

                    # Split pool into balanced teams
                    team1, team2 = [], []
                    team1_rank_value = 0
                    team2_rank_value = 0

                    # assign to pools
                    for player in pool:
                        rank_value = player.get('rank_value', 0)

                        if team1_rank_value <= team2_rank_value:
                            team1.append(player)
                            team1_rank_value += rank_value
                        else:
                            team2.append(player)
                            team2_rank_value += rank_value

                    # Record match in database
                    for player in team1:
                        user_id = player.get('user_id')
                        if user_id:
                            query = "INSERT INTO Matches(user_id, teamUp, teamId, match_num, game_name, matchmaking_session) VALUES(?, ?, ?, ?, ?, ?)"
                            db.cursor.execute(query, (user_id, "team1", match_id, match_num, "Marvel Rivals", session_id))

                    for player in team2:
                        user_id = player.get('user_id')
                        if user_id:
                            query = "INSERT INTO Matches(user_id, teamUp, teamId, match_num, game_name, matchmaking_session) VALUES(?, ?, ?, ?, ?,?)"
                            db.cursor.execute(query, (user_id, "team2", match_id, match_num, "Marvel Rivals", session_id))


                    # Create embeds for the teams
                    team1_embed = discord.Embed(
                        title=f"Game {pool_idx + 1} - Team 1 (Match ID: {match_id})",
                        color=discord.Color.blue(),
                        description=f"Game {pool_idx + 1} of {game_count}\nAverage Rank Value: {team1_rank_value:.2f}"
                    )

                    team2_embed = discord.Embed(
                        title=f"Game {pool_idx + 1} - Team 2 (Match ID: {match_id})",
                        color=discord.Color.red(),
                        description=f"Game {pool_idx + 1} of {game_count}\nAverage Rank Value: {team2_rank_value:.2f}"
                    )
                    
                    # Add players to embeds
                    for i, player in enumerate(team1):
                        name = player.get('player_name', player.get('user_id', 'Unknown'))
                        tier = f"{player.get('tier', 'unranked')}"
                        rank = f"{player.get('rank', 0)}"
                        rank_value = f"{player.get('rank_value', 0)}"
                        
                        team1_embed.add_field(
                            name=f"Player {i + 1}: {name}",
                            value=f"**Rank:** {tier} {rank}\n**Value:** {rank_value}",
                            inline=True
                        )

                    for i, player in enumerate(team2):
                        name = player.get('player_name', player.get('user_id', 'Unknown'))
                        tier = f"{player.get('tier', 'unranked')}"
                        rank = f"{player.get('rank', 0)}"
                        rank_value = f"{player.get('rank_value', 0)}"
                        
                        team2_embed.add_field(
                            name=f"Player {i + 1}: {name}",
                            value=f"**Rank:** {tier} {rank}\n**Value:** {rank_value}",
                            inline=True
                        )
                    
                    # Instructions for recording match outcome
                    instructions = (
                        f"**Marvel Rivals Matchmaking - Game {pool_idx + 1} of {game_count}**\nTeam 1 Average Rank Value: {team1_rank_value:.2f} | Team 2 Average Rank Value: {team2_rank_value:.2f}\n"
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
                            query = "INSERT INTO Matches(user_id, teamUp, teamId, match_num, game_name, matchmaking_session) VALUES(?, ?, ?, ?, ?,?)"
                            db.cursor.execute(query, (user_id, "participation", participation_id, participation_match_num, "Marvel Rivals", session_id))

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
                        rank = f"{player.get('rank', 0):.2f}%"
                        tier = f"{player.get('kda', 0):.2f}"
                        rank_value = f"{player.get('rank_value', 0):.2f}"

                        participation_embed.add_field(
                            name=f"Player {i + 1}: {name}",
                            value=f"**Rank:** {tier} {rank}\n**Value:** {rank_value}",
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
    await bot.add_cog(MarvelRivalsMatchmakingController(bot))