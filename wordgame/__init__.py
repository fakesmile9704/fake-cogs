from .wordgame import WordGame


async def setup(bot):
    await bot.add_cog(WordGame(bot))
