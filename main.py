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

        # --- STARE BOSS VIU (VERDE) ---
        if self.current_hp > 0:
            embed = discord.Embed(
                title=f"✧ CONFRUNTARE VIP: {self.boss_info['nume']} ✧",
                description=(
                    f"✧ ------------------ ✧\n\n"
                    f"Eroi în luptă: {', '.join([u.mention for u in self.participants])}\n\n"
                    f"**HP Rămas:**"
                ),
                color=0x2ECC71 
            )
            
            # Imaginea Boss (MARE)
            embed.set_image(url=self.boss_info['viu'])
            # Bara de HP (MICĂ - Sus)
            embed.set_thumbnail(url=get_hp_bar_link(self.current_hp, self.max_hp))
            
            info_text_viu = (
                f"✧ ------------------ ✧\n\n"
                f"Fiecare lovitură scade **50 HP**.\n"
                f"Loviți împreună pentru cotă maximă!"
            )
            embed.add_field(name="📦 Detalii Luptă", value=info_text_viu, inline=False)
            
            embed.set_footer(text=f"💥 Ultimul atac: {user.display_name} ➔ -50 HP", icon_url=bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        
        # --- STARE BOSS MORT (ROȘU) ---
        else:
            button.disabled = True
            button.label = "Mort!"
            button.style = discord.ButtonStyle.secondary

            drop_occurs = random.choices([True, False], weights=[25, 75], k=1)[0]
            
            embed_dead = discord.Embed(
                title=f"✧ [VENUS2] VIP DEFEATED: {self.boss_info['nume']} ✧",
                description=(
                    f"✧ ------------------ ✧\n\n"
                    f"**Rezultat Final:**"
                ),
                color=0xE74C3C 
            )
            
            # Boss Mort (MARE)
            embed_dead.set_image(url=self.boss_info['mort'])
            # Bara de 0% (MICĂ - Sus)
            embed_dead.set_thumbnail(url=HP_BAR_LINKS["0"])

            if drop_occurs:
                results_text = ""
                for p in self.participants:
                    has_tag = "[Venus2]" in p.display_name or any(role.name == "Venus2" for role in p.roles)
                    share = 150 if has_tag else 50
                    tag_status = "✨ (VIP)" if has_tag else ""
                    results_text += f"👤 {p.mention} ➔ **Recompensă:** **{share} DC** {tag_status}\n"
                
                embed_dead.description += (
                    f"\n\nBoss-ul a fost doborât și a lăsat o urmă de bogăție!\n\n"
                    f"{results_text}"
                )
            else:
                embed_dead.description += (
                    f"\n\nEroii {', '.join([u.mention for u in self.participants])} l-au ucis,\n"
                    f"dar acest boss nu avea niciun obiect de preț asupra lui.\n\n"
                    f"**Drop:** ❌ Eșuat"
                )

            info_text_mort = (
                f"✧ ------------------ ✧\n\n"
                f"🪙 **50 DC** ➔ Cota Standard\n"
                f"💎 **150 DC** ➔ Cota VIP\n\n"
                f"💡 **CUM SĂ IEI COTĂ VIP (150 DC)?**\n"
                f"*Poartă tag-ul **[Venus2]** în numele tău de server!*"
            )
            embed_dead.add_field(name="📦 Informații Drop", value=info_text_mort, inline=False)
            
            embed_dead.set_footer(text="Venus2 - Battle System Engine", icon_url=bot.user.display_avatar.url)
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
            f"**Pregătiți armele! Recompensa este aproape.**"
        ),
        color=0x2ECC71 
    )
    
    # Boss Viu (MARE)
    embed.set_image(url=boss_ales['viu'])
    # Bara de 100% (MICĂ - Sus)
    embed.set_thumbnail(url=HP_BAR_LINKS["100"])
    
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
