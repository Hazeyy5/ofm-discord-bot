import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Paris"))

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    from utils.logger import log_message
    await log_message(bot, f"✅ Bot connecté – {bot.user}")
    scheduler.start()

# Chargement automatique des cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(os.getenv("DISCORD_TOKEN"))
