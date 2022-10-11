import os
import logging
import dataset

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import Character_Bot
import utils.database as database


log = logging.getLogger(__name__)

class CharacterModal(discord.ui.Modal, title='Cohere Character Config'):
    char_name = discord.ui.TextInput(
        label="Name",
        style=discord.TextStyle.short,
        placeholder='Enter a name for your character...',
        required=True
    )

    char_desc = discord.ui.TextInput(
        label='Description',
        style=discord.TextStyle.paragraph,
        placeholder='Enter a description for your character...',
        required=True
    )

    async def on_submit(self, ctx: discord.Interaction):
        db = database.Database().get()
        settings_db: dataset.Table | None = db["settings"]
        assert settings_db is not None

        settings_db.update(
            dict(
                guild_id=ctx.guild_id,
                char_name=self.char_name,
                char_desc=self.char_desc
            ),
            ["guild_id"]
        )
        db.commit()
        db.close()

        await ctx.response.send_message(f'Character config updated!')

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        log.error(f'Error in modal: {error.__traceback__}')



class CohereCommands(commands.Cog):
    def __init__(self, bot: Character_Bot) -> None:
        self.bot = bot

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    class CohereGroup(app_commands.Group):
        pass
    cohere_group = CohereGroup(name="server", description="Server management commands", guild_ids=[int(os.environ.get("DISCORD_GUILD_ID", "DISCORD_GUILD_ID_MISSING"))])

    @cohere_group.command(name="character", description="Configures server Cohere character")
    async def character(
        self,
        ctx: discord.Interaction
    ):
        await ctx.response.send_modal(CharacterModal())
        

async def setup(bot: Character_Bot) -> None:
    await bot.add_cog(CohereCommands(bot))
    log.info("Commands loaded: cohere")