import discord
from discord.ext import commands, tasks
import asyncio
from discord import FFmpegPCMAudio
import requests
from datetime import datetime, timedelta
import os

class PrayerTimes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_path = "audio"
        self.audio_files = [
            "adhan_before.mp3",
            "adhan_time.mp3",
            "adhan_iqama.mp3"
        ]
        self.ffmpeg_path = "ffmpeg"
        self.city = "Jeddah"
        self.country = "Saudi Arabia"
        self.prayer_times = {}
        self.joined_flags = {}
        self.loop_task.start()

    def fetch_times(self):
        try:
            url = f"http://api.aladhan.com/v1/timingsByCity?city={self.city}&country={self.country}&method=4"
            data = requests.get(url).json()
            if data["code"] == 200:
                timings = data["data"]["timings"]
                self.prayer_times = {k: timings[k] for k in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]}
                for prayer in self.prayer_times:
                    self.joined_flags[prayer] = [False, False, False]
                print(f"Prayer times fetched: {self.prayer_times}")
        except Exception as e:
            print(f"Error fetching times: {e}")

    async def join_and_play(self, channel, audio_file, duration=5):
        if channel.guild.voice_client:
            return
        try:
            file_path = os.path.join(self.audio_path, audio_file)
            vc = await channel.connect()
            vc.play(FFmpegPCMAudio(file_path, executable=self.ffmpeg_path))
            await asyncio.sleep(duration)
            await vc.disconnect()
        except Exception as e:
            print(f"Error in {channel.name}: {e}")

    async def join_channels_with_audio(self, audio_file, duration=5):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                if len(channel.members) > 0:
                    await self.join_and_play(channel, audio_file, duration)

    @tasks.loop(seconds=30)
    async def loop_task(self):
        now = datetime.now()
        self.fetch_times()
        for prayer, time_str in self.prayer_times.items():
            prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if (prayer_time - timedelta(minutes=5)) <= now < (prayer_time - timedelta(minutes=4, seconds=50)):
                if not self.joined_flags[prayer][0]:
                    await self.join_channels_with_audio(self.audio_files[0])
                    self.joined_flags[prayer][0] = True
            if prayer_time <= now < (prayer_time + timedelta(seconds=10)):
                if not self.joined_flags[prayer][1]:
                    await self.join_channels_with_audio(self.audio_files[1])
                    self.joined_flags[prayer][1] = True
            if (prayer_time + timedelta(minutes=10)) <= now < (prayer_time + timedelta(minutes=10, seconds=10)):
                if not self.joined_flags[prayer][2]:
                    await self.join_channels_with_audio(self.audio_files[2], duration=3)
                    self.joined_flags[prayer][2] = True

async def setup(bot):
    await bot.add_cog(PrayerTimes(bot))
