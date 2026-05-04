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
    return "Venus2 Bot: Statistics System Online!"

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

# --- FUNCȚIE CLASAMENT ACTUALIZATĂ (MD + KILLS + DMG) ---
async def update_leaderboard():
    log_channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    lb_channel = bot.get_channel(LEADERBOARD_CHANNEL_ID) or await bot.fetch_channel(LEADERBOARD_CHANNEL_ID)
    if not log_channel or not lb_channel: return

    players = []
    async for msg in log_channel.history(limit=100):
        if msg.author == bot.user and "📊 **REGISTRUL VENUS2**" in msg.content:
            id_match = re.search(r"ID: (\d+)", msg.content)
            md_match = re.search(r"Suma Totală: \*\*(\d+)\*\* MD", msg.content)
            kill_match = re.search(r"Bossi Doborâți: \*\*(\d+)\*\*", msg.content)
            dmg_match = re.search(r"Damage Total: \*\*(\d+)\*\*", msg.content)
            
            if id_match:
                players.append({
                    "id": int(id_match.group(1)),
                    "md": int(md_match.group(1)) if md_match else 0,
                    "kills": int(kill_match.group(1)) if kill_match else 0,
                    "dmg": int(dmg_match.group(1)) if dmg_match else 0
                })

    players.sort(key=lambda x: x['md'], reverse=True)

    lb_text = "✧ ━━━━━━━━━━━━━━━━━━━━━ ✧\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players[:10]):
        emoji = medals[i] if i < 3 else "🎖️"
        lb_text += (f"{emoji} **Locul {i+1}:** <@{p['id']}>\n"
                   f"╰ MD: **{p['md']}** | SEFI UCISI: **{p['kills']}** | DMG: **{p['dmg']}**\n")
    
    if not players:
        lb_text += "*Niciun războinic nu a colectat date încă...*"
    lb_text += "✧ ━━━━━━━━━━━━━━━━━━━━━ ✧"

    lb_title = "🏆 CLASAMENTUL CAMPIONILOR DE PE VENUS2 🏆"
    lb_embed = discord.Embed(
        title=lb_title,
        description=f"⚔️ **PERSOANELE DIN TOP (MD | Kill-uri | Damage)** ⚔️\n\n{lb_text}",
        color=0xF1C40F
    )
    lb_embed.set_footer(text="Statistici actualizate în timp real")
    lb_embed.timestamp = discord.utils.utcnow()

    # Găsim și edităm mesajele (Info + Leaderboard)
    found_lb_msg = None
    async for msg in lb_channel.history(limit=20):
        if msg.author == bot.user and msg.embeds and msg.embeds[0].title == lb_title:
            found_lb_msg = msg
            break

    if found_lb_msg:
        await found_lb_msg.edit(embed=lb_embed)
    else:
        await lb_channel.send(embed=lb_embed)

# --- ACTUALIZARE LOG CU NOI STATISTICI ---
async def update_user_stats(user, add_md, add_kill, add_dmg, source_name):
    channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    if not channel: return

    found_msg = None
    async for message in channel.history(limit=100):
        if message.author == bot.user and f"ID: {user.id}" in message.content:
            found_msg = message
            break

    ts = f"<t:{int(discord.utils.utcnow().timestamp())}:R>"
    
    if found_msg:
        md_match = re.search(r"Suma Totală: \*\*(\d+)\*\* MD", found_msg.content)
        kill_match = re.search(r"Sefi Doborâți: \*\*(\d+)\*\*", found_msg.content)
        dmg_match = re.search(r"Damage Total: \*\*(\d+)\*\*", found_msg.content)

        new_md = (int(md_match.group(1)) if md_match else 0) + add_md
        new_kills = (int(kill_match.group(1)) if kill_match else 0) + add_kill
        new_dmg = (int(dmg_match.group(1)) if dmg_match else 0) + add_dmg

        content = (f"📊 **REGISTRUL VENUS2**\n👤 **FARMER:** {user.mention} | (ID: {user.id})\n"
                   f"💰 Suma Totală: **{new_md}** MD\n"
                   f"⚔️ Sefi Doborâți: **{new_kills}**\n"
                   f"💥 Damage Total: **{new_dmg}**\n"
                   f"━━━━━━━━━━━━━━━━━━\n"
                   f"📅 **Ultima victorie:** {source_name} ({ts})")
        await found_msg.edit(content=content)
    else:
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **FARMER:** {user.mention} | (ID: {user.id})\n"
                   f"💰 Suma Totală: **{add_md}** MD\n"
                   f"⚔️ Sefi Doborâți: **{add_kill}**\n"
                   f"💥 Damage Total: **{add_dmg}**\n"
                   f"━━━━━━━━━━━━━━━━━━\n"
                   f"📅 **Prima victorie:** {source_name} ({ts})")
        await channel.send(content=content)
    
    await update_leaderboard()

# --- CLASA BOSS REVIZUITĂ ---
class BossView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info = boss_info
        self.max_hp = 200
        self.current_hp = 200
        self.participants = {} # Stocăm: user -> damage_dat

    @discord.ui.button(label="Atacă Seful", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def ataca(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # Limităm la 2 jucători unici
        if user not in self.participants and len(self.participants) >= 2:
            return await interaction.response.send_message("❌ Sălașul este plin!", ephemeral=True)
        
        # Înregistrăm damage-ul
        self.participants[user] = self.participants.get(user, 0) + 50
        self.current_hp -= 50

        if self.current_hp > 0:
            mentions = ", ".join([u.mention for u in self.participants.keys()])
            embed = discord.Embed(title=f"👹 Conflict: {self.boss_info['nume']}", color=0x2ECC71,
                                description=f"🛡️ **Farmeri:** {mentions}\n\n**HP RAMAS:**\n{create_hp_bar(self.current_hp, self.max_hp)}")
            embed.set_image(url=self.boss_info['viu'])
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.stop()
            button.disabled, button.label = True, "BOSS UCIS!"
            drop = random.choices([True, False], weights=[25, 75], k=1)[0]
            embed = discord.Embed(title=f"🏆 {self.boss_info['nume']} a fost ucis!", color=0xE74C3C)
            embed.set_image(url=self.boss_info['mort'])
            
            mentions = ", ".join([u.mention for u in self.participants.keys()])
            if drop:
                res = ""
                for p, dmg in self.participants.items():
                    has_tag = "[Venus2]" in p.display_name or any(r.name == "Venus2" for r in p.roles)
                    amt = 150 if has_tag else 50
                    res += f"👤 {p.mention} ➔ **{amt} MD** (Damage: {dmg})\n"
                    # Trimitem datele: MD, 1 kill, dmg dat
                    await update_user_stats(p, amt, 1, dmg, self.boss_info['nume'])
                embed.description = f"⚔️ **Eroi:** {mentions}\n\n**DROP:**\n{res}📜 *Statistici actualizate!*"
            else:
                # Chiar dacă nu e drop, adăugăm kill-ul și damage-ul
                for p, dmg in self.participants.items():
                    await update_user_stats(p, 0, 1, dmg, self.boss_info['nume'])
                embed.description = f"⚔️ **Cine a participat la ucidere:** {mentions}\n\nSeful a murit, dar nu a dropat nimic..."
            
            await interaction.response.edit_message(embed=embed, view=self)

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
    await ctx.send("🔄 Sincronizare statistici...", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def resetlogs(ctx):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.purge(limit=100)
    await update_leaderboard()
    await ctx.send("✅ Arhivele au fost șterse!")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
