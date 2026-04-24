import discord
from discord.ui import *
from config import settings
import traceback
import asyncio
import time
from model import dbc_model
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

logger = settings.logging.getLogger("discord")

class RankSelect(discord.ui.Select):
    def __init__(self, game: str, player_id: int):
        self.game = game.lower()
        self.player_id = player_id

        if "league of legends" in self.game:
            options = [
                discord.SelectOption(label="Iron"),
                discord.SelectOption(label="Bronze"),
                discord.SelectOption(label="Silver"),
                discord.SelectOption(label="Gold"),
                discord.SelectOption(label="Platinum"),
                discord.SelectOption(label="Diamond"),
                discord.SelectOption(label="Master"),
                discord.SelectOption(label="Challenger"),
            ]

        elif "marvel rivals" in self.game:
            options = [
                discord.SelectOption(label="Bronze"),
                discord.SelectOption(label="Silver"),
                discord.SelectOption(label="Gold"),
                discord.SelectOption(label="Platinum"),
                discord.SelectOption(label="Diamond"),
                discord.SelectOption(label="Grandmaster"),
            ]

        else:
            options = [
                discord.SelectOption(label="Unranked")
            ]

        super().__init__(
            placeholder=f"Select rank for {self.game}",
            options=options,
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction: discord.Interaction):
        rank = self.values[0]

        db = dbc_model.Tournament_DB()
        cursor = db.cursor

        if self.game == "league of legends":
            cursor.execute(
                """
                UPDATE league_game_details
                SET rank = ?
                WHERE user_id IN (
                SELECT user_id FROM player WHERE user_id = ?
                )
                """,
                (rank, self.player_id)
            )   

        elif self.game == "marvel rivals":
            cursor.execute(
                """
                UPDATE mr_game_details
                SET rank = ?
                WHERE user_id IN (
                SELECT user_id FROM player WHERE user_id = ?
                )
                """,
                (rank, self.player_id)
            )   

        db.connection.commit()
        db.close_db()

        await interaction.response.send_message(
            f"Rank saved: **{rank}** for {self.game}",
            ephemeral=True
        )

class RankView(discord.ui.View):
    def __init__(self, game: str, player_id: int):
        super().__init__(timeout=120)
        self.add_item(RankSelect(game, player_id))

class GameSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select a game",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Marvel Rivals"),
                discord.SelectOption(label="Call Of Duty"),
                discord.SelectOption(label="League Of Legends"),
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        selected_game = self.values[0]
        await interaction.response.send_modal(RegisterModal(selected_game))

class GameSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(GameSelect())


class RegisterModal(discord.ui.Modal, title="Registration"):
    def __init__(self, game_name: str, timeout: int = 550):
        super().__init__()
        self.game_name = game_name  # string, no .value

        # Player Name input
        self.player_name = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Player Name",
            required=True,
            placeholder="Enter your player name"
        )

        # Tag ID input
        self.tag_id = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Your Tag ID",
            required=True,
            placeholder="Enter your tag ID"
        )

        # COD ONLY
        self.kda = discord.ui.TextInput(
            label="K/D/A (Call of Duty only)",
            required=False,
            placeholder="e.g. 1.20 / 2.5 / 0.8"
        )

        self.add_item(self.player_name)
        self.add_item(self.kda)
        self.add_item(self.tag_id)

    async def on_submit(self, interaction: discord.Interaction):
        """Handles the modal submission and database registration."""
        try:
            # Logging for debug
            logger.info(
                f"Game name {Fore.RED}{self.game_name}{Style.RESET_ALL} "
                f"and user id {Fore.RED}{self.tag_id.value.strip()}{Style.RESET_ALL}"
            )

            # Register player in database
            db = dbc_model.Tournament_DB()
            dbc_model.Player.register(
                db,
                interaction=interaction,
                gamename=self.game_name,
                playername=self.player_name.value.strip(),
                tagid=self.tag_id.value.strip(),
            )
            db.close_db()

            if self.game_name == "call of duty":

                await interaction.response.send_message(
                    f"{interaction.user.mention}, registration complete!",
                    embed=discord.Embed(
                        title="Check-in Summary",
                        description=(
                            f"**Game:** Call Of Duty\n"
                            f"**Player:** {self.player_name.value.strip()}\n"
                            f"**Tag ID:** {self.tag_id.value.strip()}\n"
                            f"**K/D/A:** {self.kda.value.strip() if self.kda.value else 'N/A'}"
                        ),
                        color=discord.Color.yellow()
                    )
                )
                return
            
            await interaction.response.send_message(
                "Registration complete. Now select your rank:",
                view=RankView(self.game_name, interaction.user.id),
                ephemeral=True
            )

        except Exception as ex:
            logger.error(f"Registration failed: {ex}")

            await interaction.response.send_message(
                "An error occurred during registration.",
                ephemeral=True
            )

            # Create a summary embed
            embed = discord.Embed(
                title="Check-in Summary",
                description=(
                    f"**Game Name:** {self.game_name}\n"
                    f"**Player Name:** {self.player_name.value.strip()}\n"
                    f"**Tag ID:** {self.tag_id.value.strip()}"
                ),
                color=discord.Color.yellow()
            )
            embed.set_author(name=str(interaction.user))

            # Send response to user
            await interaction.response.send_message(
                f"{interaction.user.mention}, you have completed registration.",
                embed=embed,
                ephemeral=False
            )

        except Exception as ex:
            logger.error(f"Registration failed: {ex}")
            await interaction.response.send_message(
                "An error occurred during registration. Please try again.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        logger.error(f"Modal error: {error}")
        traceback.print_tb(error.__traceback__)
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "An unexpected error occurred.", ephemeral=True
            )

class PreferenceSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Top Lane", value="top"),
            discord.SelectOption(label="Jungle", value="jungle"),
            discord.SelectOption(label="Mid Lane", value="mid"),
            discord.SelectOption(label="Bottom", value="bottom"),
            discord.SelectOption(label="Support", value="support"),
        ]
        super().__init__(options=options, placeholder="Select your preference in order (max 3)", max_values=3)

    async def callback(self, interaction: discord.Interaction):
        await self.view.selected_preferences(interaction, self.values)


class PlayerPrefRole(discord.ui.View):
    selected_pref = None

    def __init__(self, *, timeout=540):
        super().__init__(timeout=timeout)
        self.timeout = timeout
        self.message = None

        # Add the role preferences dropdown directly without needing an initial selection
        self.add_item(PreferenceSelect())

    async def selected_preferences(self, interaction: discord.Interaction, choices):
        try:
            # Acknowledge the interaction first
            await interaction.response.defer()

            # Save the preferences
            self.selected_pref = choices

            # Update the database
            db = dbc_model.Tournament_DB()
            dbc_model.Game.update_pref(db, interaction, self.selected_pref)
            db.close_db()

            # Create a response embed
            roles_list = ", ".join([role.capitalize() for role in choices])
            embed = discord.Embed(
                title="Role Preferences Saved",
                description=f"Your role preferences have been saved: {roles_list}",
                color=discord.Color.green()
            )

            # Send confirmation as ephemeral message (only visible to the user)
            await interaction.followup.send(embed=embed, ephemeral=True)

            # Delete the original message to clean up the chat
            try:
                # Try to delete using the stored message reference first
                if self.message:
                    await self.message.delete()
                else:
                    # If no stored message, use the interaction's message
                    await interaction.message.delete()
            except Exception as ex:
                logger.error(f"Error deleting message: {ex}")

            self.stop()
        except discord.errors.InteractionResponded:
            # If the interaction was already responded to, just continue with the logic
            logger.info("Interaction was already responded to, continuing with preference update")

            # Update the database
            db = dbc_model.Tournament_DB()
            dbc_model.Game.update_pref(db, interaction, self.selected_pref)
            db.close_db()

            # Try to delete the message
            try:
                if self.message:
                    await self.message.delete()
                else:
                    await interaction.message.delete()
            except Exception as ex:
                logger.error(f"Error deleting message in exception handler: {ex}")

            self.stop()

    # selected_role method removed - we only need role preferences now


class Checkin_RegisterModal(Modal, title="Registration"):
    def __init__(self, timeout: int = 550):
        super().__init__()
        self.timeout = timeout
        self.viewStart_time = time.time()
        self.game_name = TextInput(
            style=discord.TextStyle.long,
            label="game name:",
            max_length=500,
            required=True,
            placeholder="Game Name"
        )
        self.add_item(self.game_name)

        self.Tag_id = TextInput(
            style=discord.TextStyle.short,
            label="your tag id",
            required=True,
            placeholder="Tag ID"
        )
        self.add_item(self.Tag_id)

    async def on_submit(self, interaction: discord.Interaction):
        """ this has a summary of checkin submission
        info:
            summary will be send to feedback channel
        Args:
            discord interaction (interaction: discord.Interaction)
        """
        logger.info(f"game name {Fore.RED}{self.game_name.value}{Style.RESET_ALL} and user id is {Fore.RED}{self.Tag_id.value}{Style.RESET_ALL}")
        remaining_time = self.timeout - (time.time() - self.viewStart_time)
        try:
            db = dbc_model.Tournament_DB()
            dbc_model.Player.register(db, interaction=interaction, gamename=self.game_name,playername=self.player_name.value.strip(),
                                      tagid=self.Tag_id.value.strip())
            db.close_db()
            embed = discord.Embed(title="Checkin Summary",
                                  description=f"Game Name: {self.game_name}\n Player Name: {self.player_name.value()}\n Tag ID: {self.Tag_id.value}",
                                  color=discord.Color.yellow())
            embed.set_author(name=self.user)

            await interaction.response.send_message(f"{self.user}, you have completed registration", ephemeral=False, embed=embed)

            role_pref_view = PlayerPrefRole()
            # await interaction.response.send_message(f"{self.user}, you have completed registration", embed=embed, ephemeral=True)
            message = await interaction.followup.send(view=role_pref_view)

            await asyncio.sleep(self.timeout)
            await message.delete()

        except Exception as ex:
            print(f"it is faild on {ex}")
