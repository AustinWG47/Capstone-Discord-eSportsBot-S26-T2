import discord
import asyncio
from discord import Embed


class TournamentRunner:
    """
    Runs an interactive tournament bracket generated from AI (Ollama).
    
    Expected input format:
    [
        {
            "match_id": "match_1",
            "team1": {"team_name": str, "players": list[str]},
            "team2": {"team_name": str, "players": list[str] | None}
        }
    ]
    """

    def __init__(self, interaction: discord.Interaction, matches: list):
        self.interaction = interaction
        self.matches = matches
        self.results = {}  # match_id -> winner

    async def start(self):
        """Start running tournament matches sequentially."""
        await self.interaction.followup.send("🏆 Starting tournament...")

        for index, match in enumerate(self.matches):
            await self.run_match(index + 1, match)

        await self.finish_tournament()

    async def run_match(self, match_number: int, match: dict):
        match_id = match.get("match_id", f"match_{match_number}")

        team1 = match.get("team1")
        team2 = match.get("team2")

        # BYE handling
        if not team2:
            self.results[match_id] = team1["team_name"]
            await self.send_bye(match_number, team1)
            return

        embed = self.create_match_embed(match_number, match_id, team1, team2)

        message = await self.interaction.followup.send(embed=embed)

        # Add reactions for winner selection
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")

        winner = await self.wait_for_winner(message)

        if winner == 1:
            self.results[match_id] = team1["team_name"]
        else:
            self.results[match_id] = team2["team_name"]

        await self.interaction.followup.send(
            f"✅ Match `{match_id}` winner: **Team {winner}**"
        )

        await asyncio.sleep(1)

    async def wait_for_winner(self, message: discord.Message) -> int:
        """Wait for admin to react with winner selection."""

        def check(reaction, user):
            return (
                user == self.interaction.user and
                reaction.message.id == message.id and
                str(reaction.emoji) in ["1️⃣", "2️⃣"]
            )

        try:
            reaction, user = await self.interaction.client.wait_for(
                "reaction_add",
                timeout=300,
                check=check
            )

            return 1 if str(reaction.emoji) == "1️⃣" else 2

        except asyncio.TimeoutError:
            await self.interaction.followup.send(
                "⏱ Match timed out. Defaulting to Team 1."
            )
            return 1

    async def send_bye(self, match_number: int, team: dict):
        embed = Embed(
            title=f"Match {match_number} - BYE",
            description=f"**{team['team_name']}** advances automatically.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Players",
            value="\n".join(team.get("players", [])) or "None",
            inline=False
        )

        await self.interaction.followup.send(embed=embed)

    def create_match_embed(self, match_number, match_id, team1, team2):
        embed = Embed(
            title=f"Match {match_number}",
            description=f"Match ID: `{match_id}`",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name=f"🔵 {team1['team_name']}",
            value="\n".join(team1.get("players", [])) or "No players",
            inline=True
        )

        embed.add_field(
            name=f"🔴 {team2['team_name']}",
            value="\n".join(team2.get("players", [])) or "No players",
            inline=True
        )

        embed.set_footer(text="React 1️⃣ or 2️⃣ to choose the winner")

        return embed

    async def finish_tournament(self):
        """Announce final results."""
        summary = "\n".join(
            [f"🏆 {match}: {winner}" for match, winner in self.results.items()]
        )

        embed = Embed(
            title="🏆 Tournament Complete",
            description=summary or "No results recorded.",
            color=discord.Color.gold()
        )

        await self.interaction.followup.send(embed=embed)
