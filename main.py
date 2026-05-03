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
    return "Venus2 Bot: Log System Enabled!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- CONFIGURARE ---
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]
LOG_CHANNEL_ID = 1500547314828443770 # ID-ul canalului tău pentru baza de date

def create_hp_bar(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    bar_length = 10
    filled = int(percentage * bar_length)
    if percentage > 0.6: color_emoji = "🟩"
    elif percentage > 0.3: color_emoji = "🟨"
    else: color_emoji = "🟥"
    bar = color_emoji * filled + "⬛" * (bar_length - filled)
    return f"{bar} **{int(percentage * 100)}%**"

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
                return await interaction.response.send_message("❌ Lupta este deja ocupată!", ephemeral=True)
            self.participants.append(user)

        self.current_hp -= self.damage_per_hit

        if self.current_hp > 0:
            embed = discord.Embed(
                title=f"⚔️ [BOSS] {self.boss_info['nume']}",
                description=(
                    f"🛡️ **Eroi în luptă:** {', '.join([u.mention for u in self.participants])}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"**VIAȚĂ RĂMASĂ:**\n{create_hp_bar(self.current_hp, self.max_hp)}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"Ultima lovitură: {user.mention} (`-50 HP`)"
                ),
                color=0x2ECC71
            )
            embed.set_image(url=self.boss_info['viu'])
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        
        else:
            button.disabled = True
            button.label = "Învins!"
            button.style = discord.ButtonStyle.secondary

            drop_occurs = random.choices([True, False], weights=[25, 75], k=1)[0]
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            
            embed_dead = discord.Embed(
                title=f"💀 {self.boss_info['nume']} a fost Răpus!",
                color=0xE74C3C
            )
            embed_dead.set_image(url=self.boss_info['mort'])
            embed_dead.set_thumbnail(url=bot.user.display_avatar.url)

            if drop_occurs:
                results_text = ""
                for p in self.participants:
                    has_tag = "[Venus2]" in p.display_name or any(role.name == "Venus2" for role in p.roles)
                    share = 150 if has_tag else 50
                    results_text += f"👤 {p.mention} ➔ **{share} DC** {'✨' if has_tag else ''}\n"
                    
                    # Trimitem log-ul pe canalul "bază de date"
                    if log_channel:
                        await log_channel.send(f"📊 **LOG PREMIU:** `{p.name}` a câștigat **{share} DC** (Boss: {self.boss_info['nume']})")
                
                embed_dead.description = (
                    f"Eroii au triumfat!\n\n"
                    f"**RECOMPENSE:**\n{results_text}\n"
                    f"✅ *Premiile au fost înregistrate în baza de date.*"
                )
            else:
                embed_dead.description = (
                    f"Boss-ul a murit, dar buzunarele lui erau goale...\n"
                    f"**Drop:** ❌ Eșuat, nu prea ai noroc azi.."
                )

            embed_dead.add_field(name="📦 Informații Drop", value="🪙 **50 DC** - Standard\n💎 **150 DC** - Tag [Venus2]", inline=False)
            embed_dead.set_footer(text="Sistem de Luptă Venus2")
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
        title=f"👹 BOSS ACTIV: {boss_ales['nume']}",
        description=f"Un inamic puternic a apărut! Se pot înscrie **2 eroi**.\n\n**HP:** {create_hp_bar(200, 200)}\n━━━━━━━━━━━━━━━━━━",
        color=0x2ECC71
    )
    embed.set_image(url=boss_ales['viu'])
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
