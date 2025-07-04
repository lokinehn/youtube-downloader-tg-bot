# YouTube Downloader Telegram bot

This is simple telegram bot (written on Python with aiogram lib) that provides downloading short (less then 50MB) YouTube videos to Telegram.

# Requirements
1. Docker with docker compose plugin
2. Bot uses YT-DLP to download videos, so you need that cli installed in the same dir with bot code. That's it

# Installation
First clone repository to directory with installed yt-dlp binary.
Then build Docker Images with command:
`docker build . -t yt-downloader:v0.1`

You need to add your bot token to BOT_TOKEN environment variable.
Then just run bot with command:
`docker compose up -d`