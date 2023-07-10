from .unsplash import Unsplash


async def setup(bot):
    await bot.add_cog(Unsplash(bot))
