import discord
from redbot.core import commands, Config
import json
from redbot.core.data_manager import bundled_data_path
import random

class WordGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=927537080882561025)
        default_guild = {
            "game_channel": None,
            "last_word": ""
        }
        self.config.register_guild(**default_guild)
        self.word_list = self.load_word_list()

    @commands.mod_or_can_manage_channel()
    @commands.command()
    async def setgamechannel(self, ctx, channel: discord.TextChannel):
        await self.config.guild(ctx.guild).game_channel.set(channel.id)
        await ctx.send(f"Game channel has been set to {channel.mention}")
        await self.send_first_word(channel)

    async def send_first_word(self, channel):
        # word_list = self.load_word_list()
        if not self.word_list:
            await channel.send("Word list is empty.")
            return

        word = self.get_random_word(self.word_list)
        jumbled_word = self.jumble_word(word)
        await self.config.guild(channel.guild).last_word.set(word)
        embed = discord.Embed(title="💬・Guess the word", description=f"Unscramble the word below:", color=0x2b2d31)
        embed.set_author(name=self.bot.user.display_name ,icon_url=self.bot.user.display_avatar)
        embed.add_field(name="🔀┆Word", value=f"**{jumbled_word}**", inline=False)
        await channel.send(embed=embed, view=SkipView(self))

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        if message.author.bot:
            return

        game_channel_id = await self.config.guild(message.guild).game_channel()
        if message.channel.id != game_channel_id:
            return

        last_word = await self.config.guild(message.guild).last_word()
        if not last_word:
            return

        if message.content.lower() == last_word.lower():
            await message.add_reaction("✅")
            await self.send_next_word(message.channel)
        else:
            await message.add_reaction("❌")
    # @commands.Cog.listener()
    async def send_next_word(self, channel):
        # word_list = self.load_word_list()
        if not self.word_list:
            await channel.send("Word list is empty.")
            return

        word = self.get_random_word(self.word_list)
        jumbled_word = self.jumble_word(word)
        await self.config.guild(channel.guild).last_word.set(word)
        embed = discord.Embed(title="💬・Guess the word", description=f"Unscramble the word below:", color=0x2b2d31)
        embed.set_author(name=self.bot.user.display_name ,icon_url=self.bot.user.display_avatar)
        embed.add_field(name="🔀┆Word", value=f"**{jumbled_word}**", inline=False)
        await channel.send(embed=embed, view=SkipView(self))


    def load_word_list(self):
        if hasattr(self, "word_list"):
            return self.word_list
        word_file = bundled_data_path(self) / "word.json"
        try:
            with open(word_file) as file:
                word_list = json.load(file)
                self.word_list = word_list
                return word_list
        except (FileNotFoundError, json.JSONDecodeError):
            self.word_list = []
            return []

    def get_random_word(self, word_list):
        return random.choice(word_list)

    def jumble_word(self, word):
        word_chars = list(word)
        random.shuffle(word_chars)
        return ''.join(word_chars)
    
class SkipView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.danger)
    async def skip(self, interaction, button):
        await interaction.response.send_message("Skipped", ephemeral=True)
        await self.cog.send_next_word(interaction.channel)