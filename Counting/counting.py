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
    async def countboard(self, ctx):
        board = await self.config.guild(ctx.guild).count_board()
        if not board:
            await ctx.send("No one has counted yet.")
            return
        leaderboard = sorted(board.items(), key=lambda x: x[1], reverse=True)
        leaderboard_str = []
        for user_id, count in leaderboard:
            user = ctx.guild.get_member(user_id)
            if user:
                leaderboard_str.append(f"{user.display_name}: {count}")
        if leaderboard_str:
            await ctx.send("\n".join(leaderboard_str))
        else:
            await ctx.send("No one has counted yet.")

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
                    embed = discord.Embed(title="Counting Game", description=f"You got the count wrong! Expected count: {current_count + 1}", color=0x2b2d31)
                    embed.set_image(url="https://media.tenor.com/4BRzlmo2FroAAAAC/kendeshi-anime-smh.gif")  # Replace with the actual image URL
                    response = await message.channel.send(embed=embed)
                    await response.delete(delay=30)  # Autodelete after 5 seconds
                elif message.author.id == last_counter:
                    await message.delete()
                    embed2 = discord.Embed(title="Counting Game", description="You can't count twice!", color=0x2b2d31)
                    response = await message.channel.send(embed=embed2)
                    await response.delete(delay=30)  # Autodelete after 5 seconds
                else:
                    await guild_data.current_count.set(number)
                    await guild_data.last_counter.set(message.author.id)
                    board = await guild_data.count_board()
                    board[message.author.id] = board.get(message.author.id, 0) + 1
                    await guild_data.count_board.set(board)
                    await message.delete()
            except ValueError:
                pass