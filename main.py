import os
import discord
from discord.ext import commands
import random
from datetime import timedelta
from flask import Flask
from threading import Thread

# --- KEEP ALIVE (Să țină botul online pe Render) ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot este Online!"

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
        super().__init__(timeout=None) # Butonul nu expiră până nu e apăsat

    @discord.ui.button(label="Distruge Piatra Metin", style=discord.ButtonStyle.danger, custom_id="distruge_metin", emoji="⚔️")
    async def distruge_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # Verificări (Tag și Booster)
        has_tag = "[Venus2]" in user.display_name or any(role.name == "Venus2" for role in user.roles)
        is_booster = user.premium_since is not None

        # Șanse drop (Alegem la întâmplare una din cele 3 variante)
        # dc = 40% șansă, timeout = 30% șansă, nimic = 30% șansă
        drop_type = random.choices(["dc", "timeout", "nimic"], weights=[40, 30, 30], k=1)[0]

        # Dezactivăm butonul pentru că cineva a apăsat pe el deja
        button.disabled = True
        button.label = "Piatra a fost distrusă"
        button.style = discord.ButtonStyle.secondary
        button.emoji = "🪨"

        # Pregătim design-ul mesajului exact ca în poza ta
        embed = discord.Embed(title="🪨 Piatra Metin a Venerei distrusă", color=discord.Color.dark_theme())
        
        # Opțional: Aici poți pune un link valid către o poză cu metinul tău
        # embed.set_image(url="LINK_CATRE_POZA_CU_METIN.jpg")

        if drop_type == "dc":
            dc_amount = 300 if has_tag else 100
            embed.description = f"{user.mention} a distrus **Piatra Metin** și a eliberat 🪙 **{dc_amount} DC**."
            
        elif drop_type == "timeout":
            embed.description = f"{user.mention} a distrus **Piatra Metin** și a eliberat ⏰ **1 oră Discord timeout**."
            if not is_booster:
                try:
                    # Aplicăm timeout-ul real de 1 oră
                    timp_expirare = discord.utils.utcnow() + timedelta(hours=1)
                    await user.timeout(timp_expirare, reason="Piatra Metin a Venerei")
                except Exception:
                    # Dacă botul nu are grad suficient să-i dea timeout
                    pass 
            else:
                embed.description += "\n*Dar a scăpat pentru că este Server Booster!*"

        else:
            embed.description = f"{user.mention} a distrus **Piatra Metin** și a eliberat ❌ **Nimic...**"

        # Textul informativ fix de dedesubt (Drop Information)
        info_text = (
            "• 🪙 **100 DC** fără tag-ul serverului / **300 DC** cu tag-ul serverului\n"
            "> Tag-ul [Venus2] crește cantitatea de DC, nu șansa de drop.\n"
            "• ⏰ **1 oră Discord timeout**\n"
            "> Server Boosterii sunt imuni la timeouts.\n"
            "• ❌ **Sau nimic...**"
        )
        embed.add_field(name="📦 Informații Drop", value=info_text, inline=False)

        # Edităm mesajul original ca să apară rezultatul și butonul oprit
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop() # Oprim ascultarea altor click-uri

# --- COMANDA CARE GENEREAZĂ PIATRA ---
@bot.command()
@commands.has_permissions(administrator=True) # Doar adminii pot spawna piatra
async def metin(ctx):
    # Când scrii !metin, apare piatra așteptând să fie distrusă
    embed = discord.Embed(
        title="🔥 O Piatră Metin a apărut!",
        description="Fii primul care o distruge pentru a lua drop-ul!",
        color=discord.Color.red()
    )
    
    view = MetinView()
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
