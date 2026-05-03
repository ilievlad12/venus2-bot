import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# --- KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot: Sistemul de Bosi este Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- CONFIGURARE BOSI ---
# Aici am definit perechile de imagini primite de la tine
BOSI_DATA = [
    {
        "nume": "Căpitanul Bestie",
        "viu": "https://i.imgur.com/XgL4k0U.png",
        "mort": "https://i.imgur.com/cLaeG60.jpeg"
    },
    {
        "nume": "Chuong",
        "viu": "https://i.imgur.com/FFqWaMV.png",
        "mort": "https://i.imgur.com/3bfJjYh.jpeg"
    },
    {
        "nume": "Goo-Pae",
        "viu": "https://i.imgur.com/wDynbzc.png",
        "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"
    },
    {
        "nume": "Mahon",
        "viu": "https://i.imgur.com/uxR8aXP.png",
        "mort": "https://i.imgur.com/6rhZfxt.jpeg"
    }
]

# --- CLASA PENTRU BUTON BOSS ---
class BossView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info = boss_info

    @discord.ui.button(label="Atacă Boss-ul", style=discord.ButtonStyle.danger, custom_id="ataca_boss", emoji="⚔️")
    async def ataca_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        has_tag = "[Venus2]" in user.display_name or any(role.name == "Venus2" for role in user.roles)

        # Șanse drop (ca la Metin: 40% DC, 60% nimic)
        drop_type = random.choices(["dc", "nimic"], weights=[40, 60], k=1)[0]

        button.disabled = True
        button.label = "Învins!"
        button.style = discord.ButtonStyle.secondary
        button.emoji = "💀"

        embed = discord.Embed(
            title=f"💀 {self.boss_info['nume']} a fost răpus!",
            color=0x2ECC71 # Verde
        )
        
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_image(url=self.boss_info['mort']) # Punem poza cu boss-ul MORT

        if drop_type == "dc":
            dc_amount = 300 if has_tag else 100
            tag_bonus_text = "✨ *(Bonus VIP Aplicat)*" if has_tag else ""
            
            embed.description = (
                f"{user.mention} l-a învins pe {self.boss_info['nume']} într-o luptă epică!\n\n"
                f"**Drop obținut:**\n"
                f"🪙 **{dc_amount} DC** {tag_bonus_text}"
            )
        else:
            embed.description = (
                f"{user.mention} l-a ucis pe {self.boss_info['nume']}, dar acesta nu purta nicio comoară...\n\n"
                f"**Drop obținut:**\n"
                f"❌ **Nimic...**"
            )

        info_text = (
            "🪙 **100 DC** ➔ Recompensă Standard\n"
            "💎 **300 DC** ➔ Recompensă VIP\n\n"
            "💡 **Sfat:** Poartă tag-ul **[Venus2]** pentru recompensa VIP!"
        )
        embed.add_field(name="📦 Informații Drop", value=info_text, inline=False)
        
        embed.set_footer(text=f"Doborât de {user.display_name}", icon_url=user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

# --- COMANDA SPAWN BOSS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def boss(ctx):
    # Alegem un boss random din lista
    boss_ales = random.choice(BOSI_DATA)

    embed = discord.Embed(
        title=f"⚠️ Boss-ul {boss_ales['nume']} a apărut!",
        description=(
            f"Un dușman de temut, **{boss_ales['nume']}**, terorizează serverul!\n"
            "Cine va fi eroul care îi va pune capăt zilelor?\n\n"
            "**Pregătiți armele!** Recompensa așteaptă."
        ),
        color=0xFF4500 # Portocaliu/Rosu
    )
    
    embed.set_image(url=boss_ales['viu']) # Punem poza cu boss-ul VIU
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    view = BossView(boss_ales)
    await ctx.send(embed=embed, view=view)

# --- PASTRĂM ȘI COMANDA METIN (OPȚIONAL) ---
# (Poți lăsa aici și codul pentru piatra metin dacă vrei să ai ambele sisteme)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
