import discord
from discord.ext import commands, tasks
import asyncio
from discord import FFmpegPCMAudio
import requests
from datetime import datetime, timedelta

class PrayerTimes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_files = [
            "adhan_before.mp3",
            "adhan_time.mp3",
            "adhan_iqama.mp3"
        ]
        self.city = "Jeddah"
        self.country = "Saudi Arabia"
        self.prayer_times = {}
        self.joined_flags = {}

        self.check_prayer_times.start()

    def fetch_prayer_times(self):
        try:
            url = f"http://api.aladhan.com/v1/timingsByCity?city={self.city}&country={self.country}&method=4"
            data = requests.get(url).json()
            if data["code"] == 200:
                timings = data["data"]["timings"]
                self.prayer_times = {p: timings[p] for p in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]}
                for prayer in self.prayer_times:
                    self.joined_flags[prayer] = [False, False, False]
                print(f"Prayer times fetched: {self.prayer_times}")
        except Exception as e:
            print(f"Error fetching prayer times: {e}")

    async def join_and_play(self, channel, audio_file, duration=5):
        if channel.guild.voice_client:
            return
        try:
            vc = await channel.connect()
            vc.play(FFmpegPCMAudio(audio_file))
            await asyncio.sleep(duration)
            await vc.disconnect()
        except Exception as e:
            print(f"Error in {channel.name}: {e}")

    async def join_channels_with_members(self, audio_file, duration=5):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                if len(channel.members) > 0:
                    await self.join_and_play(channel, audio_file, duration)

    @tasks.loop(seconds=30)
    async def check_prayer_times(self):
        now = datetime.now()
        self.fetch_prayer_times()
        for prayer, time_str in self.prayer_times.items():
            prayer_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)

            # 5 mins before
            if (prayer_time - timedelta(minutes=5)) <= now < (prayer_time - timedelta(minutes=4, seconds=50)):
                if not self.joined_flags[prayer][0]:
                    await self.join_channels_with_members(self.audio_files[0], duration=5)
                    self.joined_flags[prayer][0] = True

            # At prayer time
            if prayer_time <= now < (prayer_time + timedelta(seconds=10)):
                if not self.joined_flags[prayer][1]:
                    await self.join_channels_with_members(self.audio_files[1], duration=5)
                    self.joined_flags[prayer][1] = True

            # Iqama (10 mins after)
            iqama_time = prayer_time + timedelta(minutes=10)
            if iqama_time <= now < (iqama_time + timedelta(seconds=10)):
                if not self.joined_flags[prayer][2]:
                    await self.join_channels_with_members(self.audio_files[2], duration=3)
                    self.joined_flags[prayer][2] = True

async def setup(bot):
    await bot.add_cog(PrayerTimes(bot))
