import discord
from discord.ext import commands, tasks
import asyncio
from discord import FFmpegPCMAudio

class PrayerReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_files = [
            "adhan_reminder_1.mp3",
            "adhan_reminder_2.mp3",
            "adhan_reminder_3.mp3"
        ]
        self.audio_durations = [5, 5, 3]

        self.test_join_count = 0
        self.test_max_joins = 3
        self.test_interval = 5
        self.test_joining.start()

    async def join_and_play(self, channel):
        """Join a voice channel, play audio, then disconnect."""
        if channel.guild.voice_client:  # already connected
            return
        try:
            audio_file = self.audio_files[self.test_join_count]
            play_time = self.audio_durations[self.test_join_count]

            vc = await channel.connect()
            vc.play(FFmpegPCMAudio(audio_file))  # no hardcoded ffmpeg path
            await asyncio.sleep(play_time)
            await vc.disconnect()

            print(f"Finished join #{self.test_join_count + 1} in {channel.name}")
            self.test_join_count += 1
        except Exception as e:
            print(f"Error in {channel.name}: {e}")

    async def join_channels_with_members(self, guild):
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                await self.join_and_play(channel)
                if self.test_join_count >= self.test_max_joins:
                    return

    @tasks.loop(seconds=10)
    async def test_joining(self):
        if self.test_join_count >= self.test_max_joins:
            print("Test complete. Stopping loop.")
            self.test_joining.stop()
            return
        for guild in self.bot.guilds:
            await self.join_channels_with_members(guild)
            if self.test_join_count < self.test_max_joins:
                await asyncio.sleep(self.test_interval)

async def setup(bot):
    await bot.add_cog(PrayerReminder(bot))
