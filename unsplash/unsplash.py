import discord
import random
import requests
from redbot.core import commands

class Unsplash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def uimage(self, ctx, *, query: str):
        """Get images from unsplash with a given query."""
        api_tokens = await ctx.bot.get_shared_api_tokens(service_name="unsplash")
        access_key = api_tokens.get("access_key")

        if access_key is None:
            await ctx.send(f"Sorry, no API key set. Use `{ctx.prefix}set api unsplash access_key,[ACCESS_KEY]` to set it.", )
            return

        headers = {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {access_key}"
        }

        url = f"https://api.unsplash.com/search/photos?query={query}"

        response = requests.get(url, headers=headers)
        data = response.json()

        if "results" in data:
            results = data["results"]
            if results:
                image = random.choice(results)
                image_url = image["urls"]["regular"]
                image_description = image["description"]

                embed = discord.Embed(title=query, color=0x2b2d31, description=f"**Query**: {query}\n**Description**: {image_description}")
                embed.set_image(url=image_url)

                await ctx.send(embed=embed)
            else:
                await ctx.send("No images found.")
        else:
            await ctx.send("Error retrieving images from Unsplash.")