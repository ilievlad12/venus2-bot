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
    return "Venus2 Bot: Sistemul Ultra Premium Co-op este Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- CONFIGURARE BOSI & HP BAR (LINKS) ---
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]

HP_BAR_LINKS = {
    "100": "https://i.imgur.com/LU9rg3c.gif", 
    "90": "https://i.imgur.com/wDynbzc.png", 
    "80": "https://i.imgur.com/FFqWaMV.png", 
    "70": "https://i.imgur.com/FFqWaMV.png", 
    "60": "https://i.imgur.com/FFqWaMV.png", 
    "50": "https://i.imgur.com/XgL4k0U.png", 
    "40": "https://i.imgur.com/XgL4k0U.png", 
    "30": "https://i.imgur.com/XgL4k0U.png", 
    "20": "https://i.imgur.com/XgL4k0U.png", 
    "10": "https://i.imgur.com/XgL4k0U.png", 
    "0": "https://i.imgur.com/N2wJjFl.gif"   
}

def get_hp_bar_link(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    stage = int(round(percentage * 10) * 10)
    return HP_BAR_LINKS.get(str(stage), HP_BAR_LINKS["0"])

# --- CLASA PENTRU LUPTĂ CO-OP ---
class BossCoopView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info = boss_info
        self.max_hp = 200 
        self.current_hp = 200
        self.damage_per_hit = 50
        self.participants = [] 

    @discord.ui.button(label="Atacă Boss-ul", style=discord.ButtonStyle.danger, custom_id="ataca_boss", emoji="⚔️")
    async def ataca_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        if user not in self.participants:
            if len(self.participants) >= 2:
                return await interaction.response.send_message("❌ Lupta este plină! Doar 2 jucători se pot lupta cu acest boss.", ephemeral=True)
            self.participants.append(user)

        self.current_hp -= self.damage_per_hit

        # BOSS VIU -> EMBED VERDE
        if self.current_hp > 0:
            embed = discord.Embed(
                title=f"✧ CONFRUNTARE VIP: {self.boss_info['nume']} ✧",
                description=(
                    f"✧ ------------------ ✧\n\n"
                    f"Eroi în luptă: {', '.join([u.mention for u in self.participants])}\n\n"
                    f"**HP Rămas:**"
                ),
                color=0x2ECC71 # VERDE (Viu)
            )
            
            # [CORECTAT]: Imaginea boss-ului acum e MARE (mijloc)
            embed.set_image(url=self.boss_info['viu'])
            
            # [CORECTAT]: Imaginea cu V/Bara de HP acum e MICĂ (dreapta sus)
            embed.set_thumbnail(url=get_hp_bar_link(self.current_hp, self.max_hp))
            
            info_text_viu = (
                f"✧ ------------------ ✧\n\n"
                f"Fiecare lovitură scade **50 HP**.\n"
                f"Loviți împreună pentru cotă maximă!"
            )
            embed.add_field(name="📦 Detalii Luptă", value=info_text_viu, inline=False)
            
            embed.set_footer(text=f"💥 Ultimul atac: {user.display_name} ➔ -50 HP", icon_url=bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        
        # BOSS MORT -> EMBED ROȘU
        else:
            button.disabled = True
            button.label = "Mort!"
            button.style = discord.ButtonStyle.secondary

            drop_occurs = random.choices([True, False], weights=[25, 75], k=1)[0]
            
            embed_dead = discord.Embed(
                title=f"✧ [VENUS2] VIP DEFEATED: {self.boss_info['nume']} ✧",
                description=(
