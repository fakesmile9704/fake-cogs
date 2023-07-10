from redbot.core import commands, Config
import discord

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "counting_channel": None,
            "current_count": 0,
            "count_board": {},
            "last_counter": None
        }
        self.config.register_guild(**default_guild)

    @commands.command()
    async def setcounting(self, ctx, channel: discord.TextChannel):
        await self.config.guild(ctx.guild).counting_channel.set(channel.id)
        await ctx.send(f"Counting channel has been set to {channel.mention}")

    @commands.command()
    async def currentcount(self, ctx):
        count = await self.config.guild(ctx.guild).current_count()
        await ctx.send(f"The current count is {count}")

    @commands.command()
    async def resetcountchannel(self, ctx):
        await self.config.guild(ctx.guild).counting_channel.set(None)
        await ctx.send("Counting channel has been reset.")

    @commands.command()
    async def countrules(self, ctx):
        rules = ("1: A person can't count twice in a row\n"
                 "2: The user for each number should alternate\n"
                 "3: If a number is counted wrong the count will reset")
        await ctx.send(rules)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        guild_data = self.config.guild(message.guild)
        counting_channel = await guild_data.counting_channel()
        if message.channel.id == counting_channel:
            try:
                number = int(message.content)
                current_count = await guild_data.current_count()
                last_counter = await guild_data.last_counter()
                if number != current_count + 1:
                    await message.delete()
                    await guild_data.current_count.set(0)
                    embed = discord.Embed(title="Counting Game", description=f"You got the count wrong dummy! Counting restarted from 1", color=0x2b2d31)
                    embed.set_image(url="https://media.tenor.com/4BRzlmo2FroAAAAC/kendeshi-anime-smh.gif")
                    response = await message.channel.send(embed=embed)
                    await response.delete(delay=5)
                elif message.author.id == last_counter:
                    await message.delete()
                    embed2 = discord.Embed(title="Counting Game", description="You can't count twice!", color=0x2b2d31)
                    embed2.set_image(url="https://i.pinimg.com/originals/63/c0/c6/63c0c6b632dfffd790b60a87007f1bfd.gif")
                    response = await message.channel.send(embed=embed2)
                    await response.delete(delay=5)
                else:
                    await guild_data.current_count.set(number)
                    await guild_data.last_counter.set(message.author.id)
                    board = await guild_data.count_board()
                    board[message.author.id] = board.get(message.author.id, 0) + 1
                    await guild_data.count_board.set(board)
                    await message.add_reaction("✅")
                    
            except ValueError:
                pass