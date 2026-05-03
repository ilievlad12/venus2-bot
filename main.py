import os
import discord
from discord.ext import commands
import random
from flask import Flask
from threading import Thread

# --- KEEP ALIVE (Să țină botul online pe Render) ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot este Online și Arată Superb!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- CLASA PENTRU BUTON ---
class MetinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Butonul nu expiră

    @discord.ui.button(label="Distruge Piatra Metin", style=discord.ButtonStyle.danger, custom_id="distruge_metin", emoji="⚔️")
    async def distruge_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # Verificare Tag [Venus2]
        has_tag = "[Venus2]" in user.display_name or any(role.name == "Venus2" for role in user.roles)

        # Șanse drop (40% DC, 60% nimic)
        drop_type = random.choices(["dc", "nimic"], weights=[40, 60], k=1)[0]

        # Dezactivăm butonul
        button.disabled = True
        button.label = "Sfărâmată!"
        button.style = discord.ButtonStyle.secondary
        button.emoji = "🪨"

        # ==========================================
        # [DESIGN NOU] Embed Stare DISTRUSĂ
        # ==========================================
        # Culoare: Verde Smarald (Emerald) pentru succes
        embed = discord.Embed(
            title="🏆 Piatra Metin a Venerei: Cucerită!",
            color=0x2ECC71 # Un verde rich, plăcut
        )
        
        # Adăugăm imaginea cu piatra spartă
        embed.set_image(url="https://cdn.discordapp.com/attachments/1499014597686853785/1500325757048852511/destroyed.png?ex=69f806bf&is=69f6b53f&hm=ee6d62f9915f641fa06e5c3a34e4a11f3f878cf3c34e57baa5e7438d15363ebd&")

        if drop_type == "dc":
            dc_amount = 300 if has_tag else 100
            tag_bonus_text = "(Bonus Tag [Venus2] Detectat!)" if has_tag else "(Fără Tag, Recompensă Standard)"
            
            # Descriere frumos formatată
            embed.description = (
                f"{user.mention} a demonstrat o forță incredibilă și a sfărâmat piatra!\n"
                f"Din măruntaiele ei a țâșnit aur curat:\n\n"
                f"💰 Drop: **`[ {dc_amount} DC ]`**\n"
                f"> *{tag_bonus_text}*"
            )
        else:
            embed.description = (
                f"{user.mention} a distrus Piatra Metin, dar aceasta a fost blestemată!\n"
                f"Nu a eliberat nicio recompensă de data asta...\n\n"
                f"❌ Drop: **`[ Nimic... ]`**"
            )

        # Câmp informativ curat, cu cod blocks pentru valorile cheie
        info_text = (
            f"• 🪙 Recompensă Standard: **`[ 100 DC ]`**\n"
            f"• 🌟 Recompensă cu Tag: **`[ 300 DC ]`**\n"
            f"> *Poartă tag-ul `[Venus2]` în nume sau rol pentru bonus.*"
        )
        embed.add_field(name="📦 Informații Drop Potential", value=info_text, inline=False)
        
        # Footer cu Timestamp
        embed.set_footer(text=f"Distrusă de {user.display_name}", icon_url=user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        # Edităm mesajul
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

# --- COMANDA SPAWN ---
@bot.command()
@commands.has_permissions(administrator=True) # Doar adminii pot spawna piatra
async def metin(ctx):
    # ==========================================
    # [DESIGN NOU] Embed Stare SPAWNATĂ
    # ==========================================
    # Culoare: Portocaliu Intens (OrangeRed) pentru pericol și acțiune
    embed = discord.Embed(
        title="☄️ O Nouă Piatră Metin a Căzut!",
        description=(
            "Cerul s-a întunecat și pământul s-a cutremurat.\n"
            "O piatră misterioasă plină de comori s-a prăbușit pe server.\n\n"
            "**Fii rapid!** Primul care o distruge va lua tot drop-ul!"
        ),
        color=0xFF4500 # Un portocaliu-roșu vibrant
    )
    
    # Adăugăm imaginea cu piatra întreagă (mare, în centru)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1499014597686853785/1500325793111216321/Dekorativer-Stein-264x450.png?ex=69f806c7&is=69f6b547&hm=252963a02d919fb85a9cc4befc301a5ade20364de0eb26a8131b7aab23b7a67e&")
    
    # Thumbnail mic în colț (opțional, folosesc avatarul botului)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    view = MetinView()
    await ctx.send(embed=embed, view=view)

keep_alive()
# Luăm token-ul din setările Render, nu din cod!
bot.run(os.getenv('DISCORD_TOKEN'))
