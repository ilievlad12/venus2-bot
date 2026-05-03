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
# Aici am păstrat imaginile tale și am adăugat noile bar-uri grafice
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]

# Am generat o serie de imagini pentru fiecare stagiu (Concept URL-uri)
# NOTĂ: Pentru a funcționa, va trebui să urci imaginile pe Imgur și să pui link-urile DIRECTE (.jpg/.png)
# (Am inclus link-uri placeholder pe care trebuie să le înlocuiești cu link-urile tale de Imgur)
HP_BAR_LINKS = {
    "100": "https://i.imgur.com/LU9rg3c.gif", # <LINK_IMGUR_BAR_100_percent.jpg>
    "90": "https://i.imgur.com/wDynbzc.png", # <LINK_IMGUR_BAR_90_percent.jpg>
    "80": "https://i.imgur.com/FFqWaMV.png", # <LINK_IMGUR_BAR_80_percent.jpg>
    "70": "https://i.imgur.com/FFqWaMV.png", # <LINK_IMGUR_BAR_70_percent.jpg>
    "60": "https://i.imgur.com/FFqWaMV.png", # <LINK_IMGUR_BAR_60_percent.jpg>
    "50": "https://i.imgur.com/XgL4k0U.png", # <LINK_IMGUR_BAR_50_percent.jpg>
    "40": "https://i.imgur.com/XgL4k0U.png", # <LINK_IMGUR_BAR_40_percent.jpg>
    "30": "https://i.imgur.com/XgL4k0U.png", # <LINK_IMGUR_BAR_30_percent.jpg>
    "20": "https://i.imgur.com/XgL4k0U.png", # <LINK_IMGUR_BAR_20_percent.jpg>
    "10": "https://i.imgur.com/XgL4k0U.png", # <LINK_IMGUR_BAR_10_percent.jpg>
    "0": "https://i.imgur.com/N2wJjFl.gif"   # <LINK_IMGUR_BAR_0_percent.jpg>
}

# Funcție pentru a alege link-ul corect de imagine pe baza HP-ului
def get_hp_bar_link(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    stage = int(round(percentage * 10) * 10) # 100, 90, 80 ... 0
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
                    f"**Starea Boss-ului:**"
                ),
                color=0x2ECC71 # VERDE (Viu)
            )
            
            # [MODIFICARE DESIGN]: Am eliminat textul bara și am pus IMAGINEA custom
            embed.set_image(url=get_hp_bar_link(self.current_hp, self.max_hp))
            
            embed.set_thumbnail(url=self.boss_info['viu']) # [DESIGN CHANGE]: Imaginea boss în colț
            
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

            # Șansă scăzută de drop: 25% drop, 75% nimic
            drop_occurs = random.choices([True, False], weights=[25, 75], k=1)[0]
            
            embed_dead = discord.Embed(
                title=f"✧ [VENUS2] VIP DEFEATED: {self.boss_info['nume']} ✧",
                description=(
                    f"✧ ------------------ ✧\n\n"
                    f"**Starea Finală:**"
                ),
                color=0xE74C3C # ROȘU (Mort)
            )
            
            # [MODIFICARE DESIGN]: Punem imaginea custom 0% HP
            embed_dead.set_image(url=HP_BAR_LINKS["0"])
            
            embed_dead.set_thumbnail(url=self.boss_info['mort']) # [DESIGN CHANGE]: Boss mort în colț

            if drop_occurs:
                results_text = ""
                for p in self.participants:
                    has_tag = "[Venus2]" in p.display_name or any(role.name == "Venus2" for role in p.roles)
                    share = 150 if has_tag else 50
                    tag_status = "✨ (VIP)" if has_tag else ""
                    results_text += f"👤 {p.mention} ➔ **Recompensă:** **{share} DC** {tag_status}\n"
                
                embed_dead.description += (
                    f"\n\nBoss-ul a fost măcelărit și a lăsat o comoară în urmă!\n\n"
                    f"{results_text}"
                )
            else:
                embed_dead.description += (
                    f"\n\nEroii {', '.join([u.mention for u in self.participants])} l-au ucis,\n"
                    f"dar acest boss era sărac...\n\n"
                    f"**Drop:** ❌ Eșuat"
                )

            # [MODIFICARE DESIGN]: Reformatarea informațiilor pentru lizibilitate maximă
            info_text_mort = (
                f"✧ ------------------ ✧\n\n"
                f"🪙 **50 DC** ➔ Cota Standard\n"
                f"💎 **150 DC** ➔ Cota VIP\n\n"
                f"💡 **CUM SĂ IEI COTĂ VIP (150 DC)?**\n"
                f"*Poartă tag-ul **[Venus2]** în numele tău de server (Click profil ➔ Edit Server Profile ➔ Nickname)!*"
            )
            embed_dead.add_field(name="📦 Informații Drop", value=info_text_mort, inline=False)
            
            embed_dead.set_footer(text="Venus2 - Hardcore Battle System", icon_url=bot.user.display_avatar.url)
            embed_dead.timestamp = discord.utils.utcnow()

            await interaction.response.edit_message(embed=embed_dead, view=self)
            self.stop()

# --- COMANDA BOSS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def boss(ctx):
    boss_ales = random.choice(BOSI_DATA)
    view = BossCoopView(boss_ales)

    embed = discord.Embed(
        title=f"✧ [VENUS2] BOSS APĂRUT: {boss_ales['nume']} ✧",
        description=(
            f"✧ ------------------ ✧\n\n"
            f"Un dușman de temut terorizează serverul! Se pot înscrie **maxim 2 jucători**.\n\n"
            f"**Starea Inițială:**"
        ),
        color=0x2ECC71 # VERDE (Viu)
    )
    
    # [MODIFICARE DESIGN]: Bara custom 100% HP
    embed.set_image(url=HP_BAR_LINKS["100"])
    
    embed.set_thumbnail(url=boss_ales['viu']) # [DESIGN CHANGE]: Boss viu în colț
    
    view = BossCoopView(boss_ales)
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
