import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# --- KEEP ALIVE (Pentru Render) ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot este Online - Ediția Animată!"

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
        super().__init__(timeout=None)

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

        # --- Embed Stare DISTRUSĂ (VERDE) ---
        embed = discord.Embed(
            title="🏆 Piatra Metin a Venerei: Cucerită!",
            color=0x2ECC71 # Verde smarald
        )
        
        # Pune logoul în colț (Thumbnail)
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        
        # GIF-ul VERDE pentru distrugere
        embed.set_image(url="https://i.imgur.com/N2wJjFl.gif")

        if drop_type == "dc":
            dc_amount = 300 if has_tag else 100
            tag_bonus_text = "✨ *(Bonus VIP Aplicat)*" if has_tag else ""
            
            embed.description = (
                f"{user.mention} a demonstrat o forță incredibilă și a sfărâmat piatra!\n\n"
                f"**Drop obținut:**\n"
                f"🪙 **{dc_amount} DC** {tag_bonus_text}"
            )
        else:
            embed.description = (
                f"{user.mention} a distrus Piatra Metin, dar aceasta a fost blestemată!\n\n"
                f"**Drop obținut:**\n"
                f"❌ **Nimic...**"
            )

        # Informații Drop
        info_text = (
            "🪙 **100 DC** ➔ Recompensă Standard\n"
            "💎 **300 DC** ➔ Recompensă VIP\n\n"
            "💡 **Cum să iei recompensa VIP (300 DC)?**\n"
            "*Schimbă-ți numele pe acest server (Click pe profil ➔ Edit Server Profile ➔ Nickname) și adaugă tag-ul **[Venus2]** în fața numelui tău!*"
        )
        embed.add_field(name="📦 Informații Drop", value=info_text, inline=False)
        
        # Footer
        embed.set_footer(text=f"Distrusă de {user.display_name}", icon_url=user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

# --- COMANDA SPAWN ---
@bot.command()
@commands.has_permissions(administrator=True)
async def metin(ctx):
    # --- Embed Stare SPAWNATĂ (PORTOCALIU) ---
    embed = discord.Embed(
        title="☄️ O Nouă Piatră Metin a Căzut!",
        description=(
            "Cerul s-a întunecat și pământul s-a cutremurat.\n"
            "O piatră misterioasă plină de comori s-a prăbușit pe server.\n\n"
            "**Fii rapid!** Primul care o distruge va lua tot drop-ul!"
        ),
        color=0xFF4500 # Portocaliu vibrant
    )
    
    # GIF-ul PORTOCALIU pentru spawn
    embed.set_image(url="https://i.imgur.com/UpwH6EW.gif")
    
    # Pune logoul în colț (Thumbnail)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    view = MetinView()
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
