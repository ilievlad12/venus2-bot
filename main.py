import discord
from discord.ext import commands
import random
import os
import re
from flask import Flask
from threading import Thread

# --- KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot: Live Leaderboard System Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- CONFIGURARE CANALE ---
LOG_CHANNEL_ID = 1500547314828443770         # Unde sunt log-urile individuale (baza de date)
LEADERBOARD_CHANNEL_ID = 1500629576877867150   # Unde stă mesajul cu clasamentul top 10

# --- DATE BOSI ---
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]

# --- FUNCȚIE CLASAMENT (LIVE UPDATE) ---
async def update_leaderboard():
    log_channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    lb_channel = bot.get_channel(LEADERBOARD_CHANNEL_ID) or await bot.fetch_channel(LEADERBOARD_CHANNEL_ID)
    if not log_channel or not lb_channel: return

    players = []
    # Scanăm mesajele din log-uri pentru a extrage sumele
    async for msg in log_channel.history(limit=100):
        if msg.author == bot.user and "📊 **REGISTRUL VENUS2**" in msg.content:
            id_match = re.search(r"ID: (\d+)", msg.content)
            dc_match = re.search(r"\*\*(\d+)\*\* DC", msg.content)
            if id_match and dc_match:
                players.append({"id": int(id_match.group(1)), "amount": int(dc_match.group(1))})

    # Sortăm: Suma cea mai mare sus
    players.sort(key=lambda x: x['amount'], reverse=True)

    lb_text = "✧ ━━━━━━━━━━━━━━━━━━ ✧\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players[:10]):
        emoji = medals[i] if i < 3 else "🎖️"
        lb_text += f"{emoji} **Locul {i+1}:** <@{p['id']}> ➔ **{p['amount']} DC**\n"
    
    if not players:
        lb_text += "*Arhivele sunt goale. Niciun erou înregistrat...*"
    lb_text += "\n✧ ━━━━━━━━━━━━━━━━━━ ✧"

    embed = discord.Embed(
        title="🏆 CLASAMENTUL CAMPIONILOR VENUS2 🏆",
        description=f"⚔️ **Cei mai bogați războinici ai regatului** ⚔️\n\n{lb_text}",
        color=0xF1C40F # Auriu
    )
    embed.set_footer(text="Actualizat automat la fiecare pradă")
    embed.timestamp = discord.utils.utcnow()

    # Căutăm dacă există deja mesajul de clasament ca să-i dăm EDIT
    found_lb_msg = None
    async for msg in lb_channel.history(limit=20):
        if msg.author == bot.user and msg.embeds and "🏆 CLASAMENTUL CAMPIONILOR VENUS2 🏆" in msg.embeds[0].title:
            found_lb_msg = msg
            break

    if found_lb_msg:
        await found_lb_msg.edit(embed=embed)
    else:
        await lb_channel.send(embed=embed)

# --- FUNCȚIE ACTUALIZARE LOG INDIVIDUAL ---
async def update_user_log(user, amount, source_name):
    channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    if not channel: return

    found_msg = None
    async for message in channel.history(limit=100):
        if message.author == bot.user and f"ID: {user.id}" in message.content:
            found_msg = message
            break

    ts = f"<t:{int(discord.utils.utcnow().timestamp())}:R>"
    if found_msg:
        match = re.search(r"\*\*(\d+)\*\* DC", found_msg.content)
        new_total = (int(match.group(1)) if match else 0) + amount
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
                   f"💰 **Suma Totală:** **{new_total}** DC\n⚔️ **Ultima pradă:** +{amount} DC ({source_name})\n📅 **Actualizat:** {ts}")
        await found_msg.edit(content=content)
    else:
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
                   f"💰 **Suma Totală:** **{amount}** DC\n⚔️ **Ultima pradă:** +{amount} DC ({source_name})\n📅 **Înregistrat:** {ts}")
        await channel.send(content=content)
    
    # După log, actualizăm și clasamentul general
    await update_leaderboard()

# --- HP BAR DESIGN ---
def create_hp_bar(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    filled = int(percentage * 10)
    color = "🟩" if percentage > 0.6 else "🟨" if percentage > 0.3 else "🟥"
    return f"{color * filled}{'⬛' * (10 - filled)} **{int(percentage * 100)}%**"

# --- CLASA BOSS VIEW ---
class BossView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info, self.max_hp, self.current_hp, self.participants = boss_info, 200, 200, []

    @discord.ui.button(label="Atacă Bestia", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def ataca(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user not in self.participants:
            if len(self.participants) >= 2:
                return await interaction.response.send_message("❌ Sălașul este plin!", ephemeral=True)
            self.participants.append(user)
        
        self.current_hp -= 50
        if self.current_hp > 0:
            embed = discord.Embed(title=f"👹 Conflict: {self.boss_info['nume']}", color=0x2ECC71,
                                description=f"🛡️ **Luptători:** {', '.join([u.mention for u in self.participants])}\n\n**ENERGIE:**\n{create_hp_bar(self.current_hp, self.max_hp)}")
            embed.set_image(url=self.boss_info['viu'])
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.stop()
            button.disabled, button.label = True, "Răpus!"
            drop = random.choices([True, False], weights=[25, 75], k=1)[0]
            embed = discord.Embed(title=f"🏆 {self.boss_info['nume']} a fost doborât!", color=0xE74C3C)
            embed.set_image(url=self.boss_info['mort'])
            if drop:
                res = ""
                for p in self.participants:
                    has_tag = "[Venus2]" in p.display_name or any(r.name == "Venus2" for r in p.roles)
                    amt = 150 if has_tag else 50
                    res += f"👤 {p.mention} ➔ **{amt} DC**\n"
                    await update_user_log(p, amt, self.boss_info['nume'])
                embed.description = f"**PRADĂ EXTRASTRĂ:**\n{res}\n📜 *Clasamentul a fost actualizat.*"
            else:
                embed.description = f"Bestia a murit, dar prada s-a irosit..."
            await interaction.response.edit_message(embed=embed, view=self)

# --- COMENZI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def boss(ctx):
    boss_ales = random.choice(BOSI_DATA)
    embed = discord.Embed(title=f"👹 APARIȚIE: {boss_ales['nume']}", color=0x2ECC71,
                        description=f"Se pot înscrie **2 războinici**.\n\n**ENERGIE:** {create_hp_bar(200, 200)}")
    embed.set_image(url=boss_ales['viu'])
    await ctx.send(embed=embed, view=BossView(boss_ales))

@bot.command()
@commands.has_permissions(administrator=True)
async def leaderboard(ctx):
    await update_leaderboard()
    await ctx.send("🔄 Clasamentul a fost sincronizat!", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def resetlogs(ctx):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.purge(limit=100)
    await update_leaderboard()
    await ctx.send("✅ Registrele și Clasamentul au fost resetate!")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
