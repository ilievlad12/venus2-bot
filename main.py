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
    return "Venus2 Bot: Database System Fix Online!"

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
LOG_CHANNEL_ID = 1500547314828443770 
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]

# --- FUNCȚIE BARA HP ---
def create_hp_bar(current, maximum, length=10):
    percentage = max(0, min(current / maximum, 1))
    filled = int(percentage * length)
    if percentage > 0.6: color = "🟩"
    elif percentage > 0.3: color = "🟨"
    else: color = "🟥"
    return f"{color * filled}{'⬛' * (length - filled)} **{int(percentage * 100)}%**"

# --- FUNCȚIE STACK LOGS (FIXED) ---
async def update_user_log(user, amount, source_name):
    channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    if not channel: return

    found_msg = None
    # Căutăm în ultimele 100 de mesaje
    async for message in channel.history(limit=100):
        if message.author == bot.user and f"ID: {user.id}" in message.content:
            found_msg = message
            break

    timestamp = f"<t:{int(discord.utils.utcnow().timestamp())}:R>"
    
    if found_msg:
        # Regex îmbunătățit pentru a extrage suma indiferent de formatare
        match = re.search(r"Total: \*\*(\d+)\*\*", found_msg.content)
        old_total = int(match.group(1)) if match else 0
        new_total = old_total + amount
        
        new_content = (
            f"📊 **REGISTRUL VENUS2**\n"
            f"👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
            f"💰 **Total:** **{new_total}** DC\n"
            f"⚔️ **Ultima activitate:** +{amount} DC ({source_name})\n"
            f"📅 **Actualizat:** {timestamp}"
        )
        await found_msg.edit(content=new_content)
    else:
        new_content = (
            f"📊 **REGISTRUL VENUS2**\n"
            f"👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
            f"💰 **Total:** **{amount}** DC\n"
            f"⚔️ **Ultima activitate:** +{amount} DC ({source_name})\n"
            f"📅 **Înregistrat:** {timestamp}"
        )
        await channel.send(content=new_content)

# --- CLASA BOSS CO-OP (2 JUCĂTORI) ---
class BossView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info, self.max_hp, self.current_hp = boss_info, 200, 200
        self.participants = []

    @discord.ui.button(label="Atacă Bestia", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def ataca(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user not in self.participants:
            if len(self.participants) >= 2:
                return await interaction.response.send_message("❌ Sălașul este plin!", ephemeral=True)
            self.participants.append(user)

        self.current_hp -= 50
        if self.current_hp > 0:
            embed = discord.Embed(title=f"👹 Căpetenie: {self.boss_info['nume']}", color=0x2ECC71,
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
                embed.description = f"⚔️ **Eroi:** {', '.join([u.mention for u in self.participants])}\n\n**PRADĂ:**\n{res}📜 *Baza de date actualizată.*"
            else:
                embed.description = f"Bestia a murit, dar prada s-a irosit..."
            await interaction.response.edit_message(embed=embed, view=self)

# --- CLASA WORLD BOSS (NELIMITAT) ---
class WorldBossView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.max_hp, self.current_hp, self.participants = 2000, 2000, set()

    @discord.ui.button(label="ASALT GENERAL", style=discord.ButtonStyle.danger, emoji="🔥")
    async def ataca(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.participants.add(interaction.user)
        self.current_hp -= 100
        if self.current_hp > 0:
            embed = discord.Embed(title="🌋 WORLD BOSS: Azrael", color=0x2ECC71,
                                description=f"👥 **Luptători:** `{len(self.participants)}` eroi\n\n**ENERGIE COLECTIVĂ:**\n{create_hp_bar(self.current_hp, self.max_hp, 15)}")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.stop()
            button.disabled, button.label = True, "ANICILAT!"
            res = ""
            for p in self.participants:
                has_tag = "[Venus2]" in p.display_name or any(r.name == "Venus2" for r in p.roles)
                amt = 1000 if has_tag else 500
                res += f"🛡️ {p.mention} ➔ **{amt} DC**\n"
                await update_user_log(p, amt, "World Boss")
            embed = discord.Embed(title="🎊 WORLD BOSS ÎNVINS!", description=f"**LISTA DE ONOARE:**\n{res}", color=0xE74C3C)
            await interaction.response.edit_message(embed=embed, view=self)

# --- COMENZI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def boss(ctx):
    await ctx.send(embed=discord.Embed(title="👹 Căutând o căpetenie...", color=0x2ECC71), view=BossView(random.choice(BOSI_DATA)))

@bot.command()
@commands.has_permissions(administrator=True)
async def worldboss(ctx):
    embed = discord.Embed(title="🔥 ALERTA: WORLD BOSS 🔥", description=f"**Azrael** a apărut! Mobilizarea!\n\n**ENERGIE:**\n{create_hp_bar(2000, 2000, 15)}", color=0x2ECC71)
    await ctx.send(content="@everyone", embed=embed, view=WorldBossView())

@bot.command()
@commands.has_permissions(administrator=True)
async def resetlogs(ctx):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.purge(limit=100)
    await ctx.send("✅ Registrele au fost resetate!")

@bot.command()
@commands.has_permissions(administrator=True)
async def deletelog(ctx, user_id: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    async for msg in channel.history(limit=200):
        if f"ID: {user_id}" in msg.content:
            await msg.delete()
            return await ctx.send(f"✅ Fișa ID `{user_id}` a fost ștearsă.")
    await ctx.send("❌ Nu am găsit ID-ul.")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
