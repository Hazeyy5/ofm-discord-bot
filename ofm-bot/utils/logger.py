# utils/logger.py
import discord
from datetime import datetime
from pytz import timezone

async def log_message(bot, message: str):
    channel = discord.utils.get(bot.get_all_channels(), name="logs")
    if channel:
        paris_time = datetime.now(timezone("Europe/Paris")).strftime('%d/%m/%Y %H:%M:%S')
        await channel.send(f"📝 {message} – {paris_time}")
