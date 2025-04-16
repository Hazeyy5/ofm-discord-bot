import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Fonction pour logger dans le salon logs
discord.utils.setup_logging()

async def log_message(message: str):
    channel = discord.utils.get(bot.get_all_channels(), name="logs")
    if channel:
        await channel.send(f"📝 {message}")

# Chargement automatique des cogs\async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Module chargé : {filename}")
            except Exception as e:
                print(f"❌ Erreur dans le chargement de {filename} : {e}")

@bot.event
async def on_ready():
    await load_extensions()
    print(f"✅ Bot connecté en tant que {bot.user}")
    await log_message(f"✅ Bot connecté en tant que **{bot.user}**")

@bot.event
async def on_disconnect():
    await log_message(f"❌ Bot déconnecté – {bot.user}")

# Lancement du bot
bot.run(os.getenv("DISCORD_TOKEN"))
