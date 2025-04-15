import os
from dotenv import load_dotenv

load_dotenv()  # ← charge les variables depuis .env

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import discord
from discord.ext import commands
import openai

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import io


openai.api_key = os.getenv("OPENAI_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def contrat(ctx, numero: int, *, nom: str):
    offres = {
        1: {
            "titre": "👻 GHOST MANAGEMENT",
            "commission": "50%",
            "description": [
                "Tu veux tout déléguer sans dire que tu bosses avec une agence ?",
                "On gère ton OnlyFans à 100% (contenu, DMs, ventes, analytics).",
                "✅ Tu ne t’occupes de rien",
                "✅ Tu restes discrète",
                "✅ On booste ton CA à fond"
            ]
        },
        2: {
            "titre": "🧠 COACHING & STRATÉGIE",
            "commission": "45%",
            "description": [
                "Tu es active mais tu plafonnes ?",
                "On t’aide à refaire ton compte + ta stratégie et à tout optimiser.",
                "✅ Audit complet",
                "✅ Nouveau plan d’action",
                "✅ Suivi intensif (1 mois)"
            ]
        },
        3: {
            "titre": "💎 PACK LANCEMENT & BRANDING",
            "commission": "40%",
            "description": [
                "Tu veux lancer ton OF proprement avec une image pro ?",
                "On te crée tout : branding, feed, template, stratégie.",
                "✅ Logo, bio, identité",
                "✅ Feed + contenu prêt",
                "✅ Lancement avec structure"
            ]
        }
    }

    offre = offres.get(numero)
    if not offre:
        await ctx.send("❌ Offre non trouvée. Choisis 1, 2 ou 3.")
        return

    # Créer un fichier PDF en mémoire
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y, "📄 Contrat de collaboration – Radiance Agency")

    c.setFont("Helvetica", 12)
    y -= 40
    c.drawString(100, y, f"Date : {datetime.today().strftime('%d %B %Y')}")

    y -= 30
    c.drawString(100, y, "Entre : Radiance Agency (“l’Agence”)")
    y -= 20
    c.drawString(100, y, f"Et : {nom} (“la Créatrice”)")

    y -= 40
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, y, f"Offre choisie : {offre['titre']}")
    y -= 25

    c.setFont("Helvetica", 11)
    for line in offre["description"]:
        c.drawString(100, y, line)
        y -= 18

    y -= 20
    c.drawString(100, y, f"Commission : {offre['commission']}")

    y -= 40
    c.drawString(100, y, "Signature (Agence) : ______________________")
    y -= 20
    c.drawString(100, y, "Signature (Créatrice) : ____________________")

    c.showPage()
    c.save()
    buffer.seek(0)

    await ctx.send(f"📄 Contrat généré pour **{nom}** avec l’offre **{offre['titre']}** :",
                   file=discord.File(fp=buffer, filename=f"Contrat_{nom.replace(' ', '_')}.pdf"))


@bot.command()
async def analyse(ctx, pseudo: str):
    await ctx.channel.typing()

    prompt = f"""
Tu es un recruteur d'agence OnlyFans. Analyse ce profil social basé sur son pseudo : {pseudo}.
Décris son positionnement probable, son univers, sa niche et son potentiel pour OnlyFans.
Puis génère un message de contact professionnel et naturel à lui envoyer pour proposer une collaboration avec Radiance Agency.
    """

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en recrutement OnlyFans."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.9,
        )

        reply = completion.choices[0].message["content"]

        embed = discord.Embed(
            title=f"📊 Analyse du profil {pseudo}",
            description=reply,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Analyse IA – Radiance Bot")
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("❌ Erreur lors de l’analyse.")
        print(f"Erreur GPT analyse : {e}")

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
        
        @scheduler.scheduled_job("cron", hour=10)
async def daily_check():
    channel = discord.utils.get(bot.get_all_channels(), name="direction")  # change le nom si ton salon s'appelle autrement
    if channel:
        today = datetime.now().strftime("%A %d %B %Y")
        message = (
            f"📅 **RAPPEL DU JOUR – {today}**\n\n"
            "✅ Trouver une nouvelle modèle\n"
            "✅ Finir la professionnalisation de l’agence\n"
            "✅ Finaliser le site vitrine\n"
            "✅ Shoots à prévoir :\n"
            "✅ Contenus à valider :\n"
            "✅ Suivis DMs :"
        )
        await channel.send(message)

bot.run(os.getenv("DISCORD_TOKEN"))
