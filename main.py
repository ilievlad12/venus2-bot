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
    return "Venus2 Bot: Database Cumulative Fix Online!"

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

def create_hp_bar(current, maximum, length=10):
    percentage = max(0, min(current / maximum, 1))
    filled = int(percentage * length)
    if percentage > 0.6: color = "🟩"
    elif percentage > 0.3: color = "🟨"
    else: color = "🟥"
    return f"{color * filled}{'⬛' * (length - filled)} **{int(percentage * 100)}%**"

# --- FUNCȚIE STACK LOGS (FIXED CUMULATIVE) ---
async def update_user_log(user, amount, source_name):
    channel = bot.get_channel(LOG_CHANNEL_ID) or await bot.fetch_channel(LOG_CHANNEL_ID)
    if not channel: return

    found_msg = None
    async for message in channel.history(limit=100):
        # Căutăm mesajul care conține ID-ul unic al jucătorului
        if message.author == bot.user and f"ID: {user.id}" in message.content:
            found_msg = message
            break

    timestamp = f"<t:{int(discord.utils.utcnow().timestamp())}:R>"
    
    if found_msg:
        # Căutăm orice număr care e între ** ** și e urmat de DC
        # Această metodă este mult mai sigură pentru adunare
        match = re.search(r"\*\*(\d+)\*\* DC", found_msg.content)
        
        if match:
            old_total = int(match.group(1))
            new_total = old_total + amount
        else:
            # Dacă dintr-un motiv bizar nu găsește numărul, pornim de la suma actuală
            new_total = amount
        
        new_content = (
            f"📊 **REGISTRUL VENUS2**\n"
            f"👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
            f"💰 **Suma Totală:** **{new_total}** DC\n"
            f"⚔️ **Ultima pradă:** +{amount} DC de la {source_name}\n"
            f"📅 **Actualizat:** {timestamp}"
        )
        await found_msg.edit(content=new_content)
    else:
        # Mesaj nou dacă jucătorul nu există în registru
        new_content = (
            f"📊 **REGISTRUL VENUS2**\n"
            f"👤 **Războinic:** {user.mention} | (ID: {user.id})\n"
            f"💰 **Suma Totală:** **{amount}** DC\n"
            f"⚔️ **Ultima pradă:** +{amount} DC de la {source_name}\n"
            f"📅 **Înregistrat:** {timestamp}"
        )
        await channel.send(content=new_content)

# --- CLASA BOSS CO-OP ---
class BossView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info = boss_info
        self.max_hp = 200
        self.current_hp = 200
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
            embed = discord.Embed(
                title=f"👹 Căpetenie: {self.boss_info['nume']}", 
                color=0x2ECC71,
                description=f"🛡️ **Luptători:** {', '.join([u.mention for u in self.participants])}\n\n**ENERGIE:**\n{create_hp_bar(self.current_hp, self.max_hp)}"
            )
            embed.set_image(url=self.boss_info['viu'])
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.stop()
            button.disabled = True
            button.label = "Răpus!"
            
            drop = random.choices([True, False], weights=[25, 75], k=1)[0]
            embed = discord.Embed(title=f"🏆 {self.boss_info['nume']} a fost răpus!", color=0xE74C3C)
            embed.set_image(url=self.boss_info['mort'])
            
            # AFISARE PARTICIPANTI LA FINAL
            eroi_text = ", ".join([u.mention for u in self.participants])

            if drop:
                res = ""
                for p in self.participants:
                    has_tag = "[Venus2]" in p.display_name or any(r.name == "Venus2" for r in p.roles)
                    amt = 150 if has_tag else 50
                    res += f"👤 {p.mention} ➔ **{amt} DC**\n"
                    # Aici facem adunarea în log-uri
                    await update_user_log(p, amt, self.boss_info['nume'])
                
                embed.description = (
                    f"⚔️ **Eroi participanți:** {eroi_text}\n\n"
                    f"**PRADĂ EXTRASTRĂ:**\n{res}\n"
                    f"📜 *Registrele regatului au fost actualizate.*"
                )
            else:
                embed.description = f"⚔️ **Eroi participanți:** {eroi_text}\n\nBestia a murit, dar prada s-a irosit..."
            
            await interaction.response.edit_message(embed=embed, view=self)

# --- COMENZI ADMIN ---
@bot.command()
@commands.has_permissions(administrator=True)
async def boss(ctx):
    await ctx.send(embed=discord.Embed(title="👹 Căutând o căpetenie...", color=0x2ECC71), view=BossView(random.choice(BOSI_DATA)))

@bot.command()
@commands.has_permissions(administrator=True)
async def resetlogs(ctx):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.purge(limit=100)
        await ctx.send("✅ Toate registrele au fost șterse!")

@bot.command()
@commands.has_permissions(administrator=True)
async def deletelog(ctx, user_id: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    async for msg in channel.history(limit=200):
        if f"ID: {user_id}" in msg.content:
            await msg.delete()
            return await ctx.send(f"✅ Fișa ID `{user_id}` a fost eliminată.")
    await ctx.send("❌ ID negăsit.")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
