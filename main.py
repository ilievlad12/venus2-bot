import os
import discord
from discord.ext import commands
import random
from flask import Flask
from threading import Thread

# --- KEEP ALIVE (Pentru Render) ---
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
        button.label = "Piatra a fost distrusă"
        button.style = discord.ButtonStyle.secondary
        button.emoji = "🪨"

        # Embed pentru starea DISTRUSĂ
        embed = discord.Embed(title="🪨 Piatra Metin a Venerei distrusă", color=discord.Color.dark_theme())
        
        # Imaginea cu piatra spartă
        embed.set_image(url="https://cdn.discordapp.com/attachments/1499014597686853785/1500325757048852511/destroyed.png?ex=69f806bf&is=69f6b53f&hm=ee6d62f9915f641fa06e5c3a34e4a11f3f878cf3c34e57baa5e7438d15363ebd&")

        if drop_type == "dc":
            dc_amount = 300 if has_tag else 100
            embed.description = f"{user.mention} a distrus **Piatra Metin** și a eliberat 🪙 **{dc_amount} DC**."
        else:
            embed.description = f"{user.mention} a distrus **Piatra Metin** și a eliberat ❌ **Nimic...**"

        # Info Drop
        info_text = (
            "• 🪙 **100 DC** fără tag / **300 DC** cu tag\n"
            "> Tag-ul [Venus2] oferă bonus la cantitate.\n"
            "• ❌ **Sau nimic...**"
        )
        embed.add_field(name="📦 Informații Drop", value=info_text, inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

# --- COMANDA SPAWN ---
@bot.command()
@commands.has_permissions(administrator=True)
async def metin(ctx):
    # Embed pentru starea SPAWNATĂ
    embed = discord.Embed(
        title="🔥 O Piatră Metin a apărut!",
        description="Fii primul care o distruge pentru a lua drop-ul!",
        color=discord.Color.red()
    )
    
    # Imaginea cu piatra întreagă
    embed.set_image(url="https://cdn.discordapp.com/attachments/1499014597686853785/1500325793111216321/Dekorativer-Stein-264x450.png?ex=69f806c7&is=69f6b547&hm=252963a02d919fb85a9cc4befc301a5ade20364de0eb26a8131b7aab23b7a67e&")
    
    view = MetinView()
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
