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
    return "Venus2 Bot: Sistemul Info + Leaderboard Online!"

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
LOG_CHANNEL_ID = 1500547314828443770         # Unde sunt log-urile individuale
LEADERBOARD_CHANNEL_ID = 1500629576877867150   # Unde stă clasamentul live

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

    # --- 1. MESAJUL DE INFO (GHID PERMANENT) ---
    info_title = "📜 GHID EVENIMENT: VÂNĂTOAREA DE CĂPETENII 📜"
    info_embed = discord.Embed(
        title=info_title,
        description=(
            "Pregătește-te de luptă! Iată cum funcționează evenimentul Venus2:\n\n"
            "⚔️ **Cum participi?**\n"
            "Când o căpetenie apare pe chat, fii printre primii doi care apasă butonul **Atacă Bestia**. "
            "Lupta este colectivă, iar prada se împarte între cei doi eroi!\n\n"
            "💰 **Recompense Monede Dragon (MD):**\n"
            "• **50 MD** ➔ Recompensă Standard\n"
            "• **150 MD** ➔ Recompensă VIP (Bonus de Tag)\n\n"
            "✨ **Cum obții Bonusul VIP?**\n"
            "Poartă tag-ul **[Venus2]** în numele tău de pe server (Nickname) "
            "pentru a primi automat cota maximă de **150 MD** la fiecare victorie!\n\n"
            "🏆 **Clasamentul:**\n"
            "Mai jos poți vedea topul celor mai activi vânătorii din regat. Succes!"
        ),
        color=0x3498DB # Albastru
    )
    info_embed.set_thumbnail(url=bot.user.display_avatar.url)

    # --- 2. CALCULARE DATE CLASAMENT ---
    players = []
    async for msg in log_channel.history(limit=100):
        if msg.author == bot.user and "📊 **REGISTRUL VENUS2**" in msg.content:
            id_match = re.search(r"ID: (\d+)", msg.content)
            md_match = re.search(r"\*\*(\d+)\*\* MD", msg.content)
            if id_match and md_match:
                players.append({"id": int(id_match.group(1)), "amount": int(md_match.group(1))})

    players.sort(key=lambda x: x['amount'], reverse=True)

    lb_text = "✧ ━━━━━━━━━━━━━━━━━━ ✧\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players[:10]):
        emoji = medals[i] if i < 3 else "🎖️"
        lb_text += f"{emoji} **Locul {i+1}:** <@{p['id']}> ➔ **{p['amount']} MD**\n"
    
    if not players:
        lb_text += "*Arhivele sunt goale. Niciun erou înregistrat...*"
    lb_text += "\n✧ ━━━━━━━━━━━━━━━━━━ ✧"

    lb_title = "🏆 CLASAMENTUL CAMPIONILOR DE PE VENUS2 🏆"
    lb_embed = discord.Embed(
        title=lb_title,
        description=f"⚔️ **Cei mai bogați jucători (singurii care au MD-uri înainte de deschidere)** ⚔️\n\n{lb_text}",
        color=0xF1C40F # Auriu
    )
    lb_embed.set_footer(text="Actualizat automat la fiecare pradă")
    lb_embed.timestamp = discord.utils.utcnow()

    # --- 3. ACTUALIZARE MESAJE PE CANAL ---
    found_info_msg = None
    found_lb_msg = None

    async for msg in lb_channel.history(limit=20):
        if msg.author == bot.user and msg.embeds:
            if msg.embeds[0].title == info_title:
                found_info_msg = msg
            elif msg.embeds[0].title == lb_title:
                found_lb_msg = msg

    # Trimitem sau edităm Ghidul (primul)
    if not found_info_msg:
        await lb_channel.send(embed=info_embed)
    else:
        await found_info_msg.edit(embed=info_embed)

    # Trimitem sau edităm Clasamentul (al doilea)
    if not found_lb_msg:
        await lb_channel.send(embed=lb_embed)
    else:
        await found_lb_msg.edit(embed=lb_embed)

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
        match = re.search(r"\*\*(\d+)\*\* MD", found_msg.content)
        new_total = (int(match.group(1)) if match else 0) + amount
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
                    f"💰 **Suma Totală:** **{new_total}** MD\n⚔️ **Ultima pradă:** +{amount} MD ({source_name})\n📅 **Actualizat:** {ts}")
        await found_msg.edit(content=content)
    else:
        content = (f"📊 **REGISTRUL VENUS2**\n👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
                   f"💰 **Suma Totală:** **{amount}** MD\n⚔️ **Ultima pradă:** +{amount} MD ({source_name})\n📅 **Înregistrat:** {ts}")
        await channel.send(content=content)
    
    await update_leaderboard()

# --- HP BAR ---
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
                    res += f"👤 {p.mention} ➔ **{amt} MD**\n"
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
                        description=f"Se pot înscrie **2 războinici**.\n\n**HP:** {create_hp_bar(200, 200)}")
    embed.set_image(url=boss_ales['viu'])
    await ctx.send(embed=embed, view=BossView(boss_ales))

@bot.command()
@commands.has_permissions(administrator=True)
async def leaderboard(ctx):
    await update_leaderboard()
    await ctx.send("🔄 Clasamentul și Ghidul au fost sincronizate!", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def resetlogs(ctx):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.purge(limit=100)
    await update_leaderboard()
    await ctx.send("✅ Registrele și MD-urile au fost resetate!")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
