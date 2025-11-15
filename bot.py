import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

async def main():
    async with bot:
        # Load all Cogs
        await bot.load_extension("cogs.voice_test")
        await bot.load_extension("cogs.prayer_reminder")
        await bot.load_extension("cogs.prayer_times")
        # Start bot
        await bot.start(TOKEN)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

asyncio.run(main())
