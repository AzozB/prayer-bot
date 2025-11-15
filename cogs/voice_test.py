from discord.ext import commands

class VoiceTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Joined {channel.name}")
        else:
            await ctx.send("You are not in a voice channel.")

async def setup(bot):
    await bot.add_cog(VoiceTest(bot))
