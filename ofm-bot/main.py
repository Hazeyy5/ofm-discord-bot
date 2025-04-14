from keep_alive import keep_alive
keep_alive()
import os
from dotenv import load_dotenv

load_dotenv()  # ← charge les variables depuis .env

import discord
from discord.ext import commands
import openai

openai.api_key = os.getenv("OPENAI_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

keep_alive()  # seulement si tu utilises le système anti-sleep de Replit

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def setup_agence(ctx):
    guild = ctx.guild

    await ctx.send("🔧 Création des rôles...")

    role_data = {
        "👑 Direction": discord.Colour.dark_gold(),
        "🧑‍💼 Manager": discord.Colour.blue(),
        "🧰 Assistant": discord.Colour.green(),
        "🔥 Modèle": discord.Colour.red(),
        "👀 Visiteur": discord.Colour.light_grey(),
        "🤖 Bot": discord.Colour.purple()
    }

    roles = {}
    for name, color in role_data.items():
        existing = discord.utils.get(guild.roles, name=name)
        if existing:
            roles[name] = existing
        else:
            roles[name] = await guild.create_role(name=name, colour=color)

    await ctx.send("✅ Rôles créés !\n🔧 Création des salons...")

    everyone = guild.default_role  # @everyone

    categories = {
        "🧠 Direction": {
            "channels": ["annonces", "planning", "briefing"],
            "role": roles["👑 Direction"]
        },
        "💬 Équipe": {
            "channels": ["général", "modèles", "assistants", "managers"],
            "role": None  # Public
        },
        "📸 Contenu": {
            "channels": ["photos-à-publier", "vidéos-à-valider", "contenus-schedule", "contenus-custom"],
            "role": None
        },
        "📈 Performance": {
            "channels": ["statistiques", "feedbacks-clients", "objectifs"],
            "role": None
        },
        "🤖 Automations": {
            "channels": ["générateur-bio", "idées-légendes", "commandes-ai"],
            "role": None
        }
    }

    for cat_name, cat_info in categories.items():
        role = cat_info["role"]
        if role:
            overwrites = {
                everyone: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
        else:
            overwrites = None

        category = await guild.create_category(cat_name, overwrites=overwrites)

        for chan_name in cat_info["channels"]:
            await guild.create_text_channel(chan_name, category=category)

    await ctx.send("✅ Structure avec rôles et permissions créée avec succès !")


# 💬 Gestion des messages pour les commandes personnalisées
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    channel = message.channel.name

    if channel == "générateur-bio":
        await handle_bio(message, content)

    elif content.startswith("!bio"):
        await handle_bio(message, content[5:])

    elif content.startswith("!légende"):
        await handle_legende(message, content[9:])

    elif content.startswith("!idée-contenu"):
        await handle_idee_contenu(message, content[15:])

        # Salon général de discussion avec ChatGPT
    elif channel == "gpt-chat":
        await handle_gpt_chat(message, content)

    try:
        await bot.process_commands(message)
    except commands.CommandNotFound:
        pass


# ✨ Fonctions pour générer les contenus via ChatGPT
async def handle_bio(message, prompt):
    await message.channel.typing()
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en bios sexy, originales et percutantes pour OnlyFans et les réseaux sociaux."},
                {"role": "user", "content": f"Génère une bio en fonction de ce contexte : {prompt}"}
            ],
            max_tokens=200,
            temperature=0.85,
        )
        response = completion.choices[0].message["content"]

        embed = discord.Embed(
            title="💡 Bio générée",
            description=response,
            color=discord.Color.purple()
        )
        embed.set_footer(text="Généré par GPT-3.5 – OFM Bot")
        await message.channel.send(embed=embed)

    except Exception as e:
        await message.channel.send("❌ Erreur lors de la génération de la bio.")
        print(f"Erreur : {e}")


async def handle_legende(message, prompt):
    await message.channel.typing()
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un community manager spécialisé dans les légendes sexy et engageantes pour photos ou vidéos OnlyFans et Instagram."},
                {"role": "user", "content": f"Génère une légende accrocheuse pour ce contenu : {prompt}"}
            ],
            max_tokens=150,
            temperature=0.9,
        )
        response = completion.choices[0].message["content"]

        embed = discord.Embed(
            title="📸 Légende générée",
            description=response,
            color=discord.Color.orange()
        )
        embed.set_footer(text="Généré par GPT-3.5 – OFM Bot")
        await message.channel.send(embed=embed)

    except Exception as e:
        await message.channel.send("❌ Erreur lors de la génération de la légende.")
        print(f"Erreur : {e}")


async def handle_idee_contenu(message, prompt):
    await message.channel.typing()
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un coach en stratégie de contenu sexy pour créateurs OnlyFans."},
                {"role": "user", "content": f"Donne-moi une idée de contenu dans le thème : {prompt}"}
            ],
            max_tokens=150,
            temperature=0.8,
        )
        response = completion.choices[0].message["content"]

        embed = discord.Embed(
            title="🎬 Idée de contenu",
            description=response,
            color=discord.Color.green()
        )
        embed.set_footer(text="Généré par GPT-3.5 – OFM Bot")
        await message.channel.send(embed=embed)

    except Exception as e:
        await message.channel.send("❌ Erreur lors de la génération de l'idée.")
        print(f"Erreur : {e}")

async def handle_gpt_chat(message, prompt):
    await message.channel.typing()
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant intelligent, amical et professionnel, prêt à répondre à toutes les questions posées sur le serveur Discord."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.8,
        )
        response = completion.choices[0].message["content"]

        embed = discord.Embed(
            title="💬 Réponse de ChatGPT",
            description=response,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Généré par GPT-3.5 – OFM Bot")
        await message.channel.send(embed=embed)

    except Exception as e:
        await message.channel.send("❌ Erreur lors de la réponse.")
        print(f"Erreur GPT chat : {e}")

bot.run(os.getenv("DISCORD_TOKEN"))