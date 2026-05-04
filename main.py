import discord
from discord.ext import commands
import random
import os
import re
import asyncio
from flask import Flask
from threading import Thread

# --- KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot: Ultra Optimized System Online!"

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
LOG_CHANNEL_ID = 1500547314828443770         
LEADERBOARD_CHANNEL_ID = 1500629576877867150   
CHAT_CHANNEL_LINK = "<#1499567665813913782>"

# --- DATE BOSI ---
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]

# --- FUNCȚIE CLASAMENT + GHID (OPTIMIZATĂ) ---
async def update_leaderboard():
    log_channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    lb_channel = bot.get_channel(LEADERBOARD_CHANNEL_ID) or await bot.fetch_channel(LEADERBOARD_CHANNEL_ID)
    if not log_channel or not lb_channel: return

    # 1. GHIDUL
    info_title = "📜 GHID EVENIMENT: VÂNĂTOAREA DE CĂPETENII 📜"
    info_embed = discord.Embed(
        title=info_title,
        description=(
            f"Fii cel mai rapid vânător de pe {CHAT_CHANNEL_LINK}!\n\n"
            "⚔️ **Reguli:** Maxim 2 participanți per asediu.\n"
            "💥 **Critice:** Ai 10% șansă de Lovitură Critică (Double Damage)!\n"
            "💰 **Premii:** 50 MD (Standard) / 150 MD (Tag [Venus2])\n"
            "🏆 **Top:** Clasamentul de mai jos se actualizează live."
        ),
        color=0x3498DB
    )

    # 2. DATE CLASAMENT
    players = []
    async for msg in log_channel.history(limit=50): # Limită mică pentru viteză
        if msg.author == bot.user and "📊 **REGISTRUL VENUS2**" in msg.content:
            id_m = re.search(r"ID: (\d+)", msg.content)
            md_m = re.search(r"Suma Totală: \*\*(\d+)\*\* MD", msg.content)
            kill_m = re.search(r"Sefi Doborâți: \*\*(\d+)\*\*", msg.content)
            dmg_m = re.search(r"Damage Total: \*\*(\d+)\*\*", msg.content)
            if id_m:
                players.append({
                    "id": int(id_m.group(1)),
                    "md": int(md_m.group(1)) if md_m else 0,
                    "kills": int(kill_m.group(1)) if kill_m else 0,
                    "dmg": int(dmg_m.group(1)) if dmg_m else 0
                })

    players.sort(key=lambda x: x['md'], reverse=True)
    lb_text = "✧ ━━━━━━━━━━━━━━━━━━━━━ ✧\n"
    for i, p in enumerate(players[:10]):
        emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else "🎖️"
        lb_text += f"{emoji} **Locul {i+1}:** <@{p['id']}>\n╰ MD: **{p['md']}** | SEFI: **{p['kills']}** | DMG: **{p['dmg']}**\n"
    
    lb_title = "🏆 CLASAMENTUL CAMPIONILOR DE PE VENUS2 🏆"
    lb_embed = discord.Embed(title=lb_title, description=f"⚔️ **TOP RĂZBOINICI** ⚔️\n\n{lb_text if players else '*Gol...*'}", color=0xF1C40F)
    lb_embed.set_footer(text="Actualizat Live")

    # 3. EDIT/SEND
    found_info, found_lb = None, None
    async for msg in lb_channel.history(limit=10):
        if msg.author == bot.user and msg.embeds:
            if msg.embeds[0].title == info_title: found_info = msg
            elif msg.embeds[0].title == lb_title: found_lb = msg

    if found_info: await found_info.edit(embed=info_embed)
    else: await lb_channel.send(embed=info_embed)
    
    if found_lb: await found_lb.edit(embed=lb_embed)
    else: await lb_channel.send(embed=lb_embed)

# --- ACTUALIZARE LOG ---
async def update_user_stats(user, add_md, add_kill, add_dmg, source_name):
    channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    if not channel: return
    found_msg = None
    async for message in channel.history(limit=50):
        if message.author == bot.user and f"ID: {user.id}" in message.content:
            found_msg = message
            break
    
    ts = f"<t:{int(discord.utils.utcnow().timestamp())}:R>"
    md, kills, dmg = add_md, add_kill, add_dmg

    if found_msg:
        m_md = re.search(r"Suma Totală: \*\*(\d+)\*\* MD", found_msg.content)
        m_k = re.search(r"Sefi Doborâți: \*\*(\d+)\*\*", found_msg.content)
        m_d = re.search(r"Damage Total: \*\*(\d+)\*\*", found_msg.content)
        md += int(m_md.group(1)) if m_md else 0
        kills += int(m_k.group(1)) if m_k else 0
        dmg += int(m_d.group(1)) if m_d else 0
        
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **FARMER:** {user.mention} | (ID: {user.id})\n"
                   f"💰 Suma Totală: **{md}** MD\n⚔️ Sefi Doborâți: **{kills}**\n💥 Damage Total: **{dmg}**\n"
                   f"━━━━━━━━━━━━━━━━━━\n📅 **Ultima victorie:** {source_name} ({ts})")
        await found_msg.edit(content=content)
    else:
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **FARMER:** {user.mention} | (ID: {user.id})\n"
                   f"💰 Suma Totală: **{md}** MD\n⚔️ Sefi Doborâți: **{kills}**\n💥 Damage Total: **{dmg}**\n"
                   f"━━━━━━━━━━━━━━━━━━\n📅 **Prima victorie:** {source_name} ({ts})")
        await channel.send(content=content)
    await update_leaderboard()

# --- CLASA BOSS (ANTI-BUG & CRITICE) ---
class BossView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info, self.max_hp, self.current_hp = boss_info, 200, 200
        self.participants = {}
        self.is_processing = False # Blocaj pentru procesare finală

    @discord.ui.button(label="Atacă Seful", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def ataca(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() # REZOLVĂ INTERACTION FAILED
        
        if self.is_processing: return

        user = interaction.user
        if user not in self.participants and len(self.participants) >= 2: return

        # MECANICĂ CRITICĂ (10% șansă)
        is_crit = random.random() < 0.10
        dmg = 100 if is_crit else 50
        
        self.participants[user] = self.participants.get(user, 0) + dmg
        self.current_hp = max(0, self.current_hp - dmg)

        if self.current_hp > 0:
            mentions = ", ".join([u.mention for u in self.participants.keys()])
            crit_msg = f"\n✨ **{user.display_name} a dat o CRITICĂ!**" if is_crit else ""
            embed = discord.Embed(title=f"👹 Conflict: {self.boss_info['nume']}", color=0x2ECC71,
                                description=f"🛡️ **Farmeri:** {mentions}{crit_msg}\n\n**HP RAMAS:**\n{create_hp_bar(self.current_hp, self.max_hp)}")
            embed.set_image(url=self.boss_info['viu'])
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            self.is_processing = True # Stop atacuri
            self.stop()
            button.disabled, button.label = True, "BOSS UCIS!"
            drop = random.choices([True, False], weights=[25, 75], k=1)[0]
            embed = discord.Embed(title=f"🏆 {self.boss_info['nume']} a fost ucis!", color=0xE74C3C)
            embed.set_image(url=self.boss_info['mort'])
            
            res = ""
            for p, d in self.participants.items():
                tag = "[Venus2]" in p.display_name or any(r.name == "Venus2" for r in p.roles)
                amt = 150 if tag and drop else (50 if drop else 0)
                res += f"👤 {p.mention} ➔ **{amt} MD** (Dmg: {d})\n"
                await update_user_stats(p, amt, 1, d, self.boss_info['nume'])
            
            embed.description = f"⚔️ **Cine a participat:** {', '.join([u.mention for u in self.participants.keys()])}\n\n" + (f"**DROP:**\n{res}" if drop else "Seful a murit, dar nu a dropat nimic...")
            await interaction.edit_original_response(embed=embed, view=None)

def create_hp_bar(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    filled = int(percentage * 10)
    color = "🟩" if percentage > 0.6 else "🟨" if percentage > 0.3 else "🟥"
    return f"{color * filled}{'⬛' * (10 - filled)} **{int(percentage * 100)}%**"

# --- COMENZI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def boss(ctx):
    boss_ales = random.choice(BOSI_DATA)
    embed = discord.Embed(title=f"👹 APARIȚIE: {boss_ales['nume']}", color=0x2ECC71,
                        description=f"Se pot înscrie **2 farmeri**.\n\n**HP RAMAS:** {create_hp_bar(200, 200)}")
    embed.set_image(url=boss_ales['viu'])
    await ctx.send(embed=embed, view=BossView(boss_ales))

@bot.command()
@commands.has_permissions(administrator=True)
async def leaderboard(ctx):
    await update_leaderboard()
    await ctx.send("🔄 Sincronizare...", delete_after=3)

@bot.command()
@commands.has_permissions(administrator=True)
async def resetlogs(ctx):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.purge(limit=100)
    await update_leaderboard()
    await ctx.send("✅ Arhive resetate!")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
