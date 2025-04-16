# 📁 cogs/contrat.py
import discord
from discord.ext import commands
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import io

class Contrat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def contrat(self, ctx, numero: int, *, nom: str):
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
                "titre": "🧐 COACHING & STRATÉGIE",
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

        await ctx.send(
            f"📄 Contrat généré pour **{nom}** avec l’offre **{offre['titre']}** :",
            file=discord.File(fp=buffer, filename=f"Contrat_{nom.replace(' ', '_')}.pdf")
        )

def setup(bot):
    bot.add_cog(Contrat(bot))

