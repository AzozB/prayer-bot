import discord
from discord.ext import commands, tasks
import asyncio
from discord import FFmpegPCMAudio
import os

class PrayerReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_path = "audio"
        self.audio_files = [
            "adhan_reminder_1.mp3",
            "adhan_reminder_2.mp3",
            "adhan_reminder_3.mp3"
        ]
        self.audio_durations = [5, 5, 3]

        self.test_count = 0
        self.max_tests = 3
        self.test_interval = 5
        self.test_loop.start()

    async def join_and_play(self, channel, file_index):
        if channel.guild.voice_client:
            return
        try:
            ffmpeg_path = "ffmpeg"  # Railway-compatible
            audio_file = os.path.join(self.audio_path, self.audio_files[file_index])
            vc = await channel.connect()
            vc.play(FFmpegPCMAudio(audio_file, executable=ffmpeg_path))
            await asyncio.sleep(self.audio_durations[file_index])
            await vc.disconnect()
            print(f"Played {self.audio_files[file_index]} in {channel.name}")
        except Exception as e:
            print(f"Error: {e}")

    async def join_channels(self, guild):
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                await self.join_and_play(channel, self.test_count)
                self.test_count += 1
                if self.test_count >= self.max_tests:
                    return

    @tasks.loop(seconds=10)
    async def test_loop(self):
        if self.test_count >= self.max_tests:
            print("Test complete")
            self.test_loop.stop()
            return
        for guild in self.bot.guilds:
            await self.join_channels(guild)
            if self.test_count < self.max_tests:
                await asyncio.sleep(self.test_interval)

async def setup(bot):
    await bot.add_cog(PrayerReminder(bot))
