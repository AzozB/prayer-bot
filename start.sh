#!/bin/sh
# Install ffmpeg
apt-get update
apt-get install -y ffmpeg

# Start the bot
python bot.py
