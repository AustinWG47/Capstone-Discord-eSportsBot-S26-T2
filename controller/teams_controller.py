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

# select menu for team creation
class UserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select up to 4 users", min_values=1, max_values=4)

    async def callback(self, interaction: discord.Interaction):
        # ❌ Already owns a team
        owner_team = teams_db.get_team_of_user(interaction.user.id)
        if owner_team and owner_team[3] == interaction.user.id:  # owner_id index
            await interaction.response.send_message("❌ You already own a team.", ephemeral=True)
            return

        # Create team
        team_id = teams_db.create_team(interaction.user.id)

        success, failed = [], []

        for user in self.values:
            if user.bot:
                failed.append(user.name)
                continue
            try:
                view = InviteView(interaction.user.id, team_id)
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


class UserSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(UserSelect())

# invitation view for team invites
class InviteView(discord.ui.View):
    def __init__(self, inviter_id: int, team_id: int):
        super().__init__(timeout=900)
        self.inviter_id = inviter_id
        self.team_id = team_id

    @discord.ui.button(label="Join Team", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ❌ Already in a team
        if teams_db.get_team_of_user(interaction.user.id):
            await interaction.response.send_message("❌ You are already in a team.", ephemeral=True)
            return

        # ❌ Team full
        if teams_db.get_team_size(self.team_id) >= 4:
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

#cogs and cog setup
class TeamsManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="team_create", description="Create a team and invite users")
    async def team_create(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Select users to invite:",
            view=UserSelectView(),
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