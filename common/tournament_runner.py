import discord
from discord import Embed


class MatchView(discord.ui.View):
    def __init__(self, team1, team2, user):
        super().__init__(timeout=300)
        self.team1 = team1
        self.team2 = team2
        self.user = user
        self.winner = None

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.user

    @discord.ui.button(label="Team 1 Wins", style=discord.ButtonStyle.primary)
    async def team1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = 1
        self.stop()
        try:
            await interaction.response.defer()
        except:
            pass

    @discord.ui.button(label="Team 2 Wins", style=discord.ButtonStyle.danger)
    async def team2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = 2
        self.stop()
        try:
            await interaction.response.defer()
        except:
            pass


class TournamentRunner:

    def __init__(self, interaction: discord.Interaction, matches: list):
        self.interaction = interaction
        self.current_matches = matches  # seeded bracket
        self.results = {}

    async def start(self):

        await self.interaction.followup.send("🏆 **Tournament Starting**")

        round_number = 1
        matches = self.current_matches

        while True:

            await self.interaction.followup.send(
                f"⚔️ **Round {round_number}**"
            )

            winners = []
            next_round_matches = []

            match_number = 1

            for match in matches:

                team1 = match["team1"]
                team2 = match.get("team2")

                winner = await self.run_match(
                    round_number,
                    match_number,
                    team1,
                    team2
                )

                winners.append(winner)
                match_number += 1

            #If only one winner → tournament done
            if len(winners) == 1:
                champion = winners[0]
                await self.send_champion(champion)
                return

            #Build next round from winners
            for i in range(0, len(winners), 2):

                team1 = winners[i]
                team2 = winners[i + 1] if i + 1 < len(winners) else None

                next_round_matches.append({
                    "team1": team1,
                    "team2": team2
                })

            matches = next_round_matches
            round_number += 1

    async def run_match(self, round_number, match_number, team1, team2):

        match_id = f"round{round_number}_match{match_number}"

        #BYE handling
        if not team2:
            embed = Embed(
                title=f"Round {round_number} - Match {match_number}",
                description=f"**{team1['team_name']}** advances with a BYE.",
                color=discord.Color.green()
            )

            embed.add_field(
                name="Players",
                value="\n".join(team1.get("players", [])),
                inline=False
            )

            await self.interaction.followup.send(embed=embed)

            self.results[match_id] = team1["team_name"]
            return team1

        embed = self.create_match_embed(round_number, match_number, team1, team2)

        view = MatchView(team1, team2, self.interaction.user)

        message = await self.interaction.followup.send(embed=embed, view=view)

        await view.wait()

        winner = view.winner if view.winner else 1
        winning_team = team1 if winner == 1 else team2

        self.results[match_id] = winning_team["team_name"]

        embed.add_field(
            name="🏆 Winner",
            value=winning_team["team_name"],
            inline=False
        )

        await message.edit(embed=embed, view=view)

        return winning_team

    async def send_champion(self, champion):

        embed = Embed(
            title="🏆 Tournament Champion",
            description=f"**{champion['team_name']}** wins the tournament!",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="Players",
            value="\n".join(champion.get("players", [])),
            inline=False
        )

        await self.interaction.followup.send(embed=embed)

    def create_match_embed(self, round_number, match_number, team1, team2):

        embed = Embed(
            title=f"Round {round_number} - Match {match_number}",
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

        embed.set_footer(text="Click a button to choose the winner")

        return embed