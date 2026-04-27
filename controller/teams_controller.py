import discord
from discord import app_commands
from discord.ext import commands
from model.dbc_model import Teams

# setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Create a DB instance
teams_db = Teams()
teams_db.createTable()  # ensure tables exist

# events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    try:
        synced = await app_commands.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

def get_team_limit(game: str) -> int:
    return 5 if game == "League Of Legends" else 6

class TeamNameModal(discord.ui.Modal, title="Create Team"):
    team_name = discord.ui.TextInput(
        label="Team Name",
        placeholder="Enter your team name",
        max_length=32
    )

    def __init__(self, game: str):
        super().__init__()
        self.game = game

    async def on_submit(self, interaction: discord.Interaction):
        max_invites = get_team_limit(self.game) - 1

        view = UserSelectView(
            game=self.game,
            team_name=self.team_name.value,
            max_invites=max_invites
        )

        await interaction.response.send_message(
            f"{self.game}\n {self.team_name.value}\nSelect users:",
            view=view,
            ephemeral=True
        )

class TeamGameSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(TeamGameSelect())

class TeamGameSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select a game for your team",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Marvel Rivals"),
                discord.SelectOption(label="Call Of Duty"),
                discord.SelectOption(label="League Of Legends"),
            ]
        )
    async def callback(self, interaction: discord.Interaction):
        game = self.values[0]
        await interaction.response.send_modal(TeamNameModal(game))

class UserSelectView(discord.ui.View):
    def __init__(self, game: str, team_name: str, max_invites: int):
        super().__init__(timeout=60)
        self.game = game
        self.team_name = team_name
        self.add_item(UserSelect(game, team_name, max_invites))

# invitation view for team invites
class InviteView(discord.ui.View):
    def __init__(self, inviter_id: int, team_id: int, game: str):
        super().__init__(timeout=900)
        self.inviter_id = inviter_id
        self.team_id = team_id
        self.game = game

    @discord.ui.button(label="Join Team", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ❌ Already in a team
        if teams_db.get_team_of_user(interaction.user.id):
            await interaction.response.send_message("❌ You are already in a team.", ephemeral=True)
            return

        # ❌ Team full
        max_size = get_team_limit(self.game)

        if teams_db.get_team_size(self.team_id) >= max_size:
            await interaction.response.send_message("❌ Team is full.", ephemeral=True)
            return

        teams_db.add_member(self.team_id, interaction.user.id)

        await interaction.response.edit_message(
            content="✅ You joined the team!",
            view=None
        )

        # Notify inviter
        inviter = await interaction.client.fetch_user(self.inviter_id)
        await inviter.send(f"🎉 {interaction.user.name} joined your team!")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❌ You declined the invite.",
            view=None
        )


# select menu for team creation
class UserSelect(discord.ui.UserSelect):
    def __init__(self, game: str, team_name: str, max_invites: int):
        self.game = game
        self.team_name = team_name
        self.max_invites = max_invites

        super().__init__(
            placeholder=f"Select up to {max_invites} users",
            min_values=1,
            max_values=max_invites
        )


    async def callback(self, interaction: discord.Interaction):
        # ❌ Already owns a team
        owner_team = teams_db.get_team_of_user(interaction.user.id)
        if owner_team and owner_team[3] == interaction.user.id:  # owner_id index
            await interaction.response.send_message("❌ You already own a team.", ephemeral=True)
            return

        # Create teamm and add owner as first member
        team_id = teams_db.create_team(
            interaction.user.id,
            team_name=self.team_name,
            game_name=self.game
        )
        teams_db.add_member(team_id, interaction.user.id)

        success, failed = [], []

        for user in self.values:
            if user.bot:
                failed.append(user.name)
                continue
            try:
                view = InviteView(interaction.user.id, team_id, self.game)
                await user.send(
                    f"👥 {interaction.user.name} invited you to join their team!",
                    view=view
                )
                success.append(user.name)
            except:
                failed.append(user.name)

        await interaction.response.edit_message(
            content=f"✅ Team created!\n\nInvited: {', '.join(success) or 'None'}\nFailed: {', '.join(failed) or 'None'}",
            view=None
        )


    #cogs and cog setup
class TeamsManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="team_create", description="Create a team and invite users")
    async def team_create(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            "🎮 Select a game for your team:",
            view=TeamGameSelectView(),
            ephemeral=True
        )

    @app_commands.command(name="team_leave", description="Leave your team")
    async def team_leave(self, interaction: discord.Interaction):
        team = teams_db.get_team_of_user(interaction.user.id)
        if not team:
            await interaction.response.send_message("❌ You are not in a team.", ephemeral=True)
            return
        # Cannot remove owner
        if team[3] == interaction.user.id:  # owner_id
            await interaction.response.send_message("❌ You cannot leave your own team!", ephemeral=True)
            return
        teams_db.remove_member(team[0], interaction.user.id)
        await interaction.response.send_message("👋 You left the team.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TeamsManagement(bot))