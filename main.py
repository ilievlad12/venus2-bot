import discord
from discord.ext import commands
import random
import os
import re # Avem nevoie de asta pentru a extrage numerele din text
from flask import Flask
from threading import Thread

# --- KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home():
    return "Venus2 Bot: Stackable Database System Online!"

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
LOG_CHANNEL_ID = 1500547314828443770 

def create_hp_bar(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    bar_length = 10
    filled = int(percentage * bar_length)
    if percentage > 0.6: color_emoji = "🟩"
    elif percentage > 0.3: color_emoji = "🟨"
    else: color_emoji = "🟥"
    bar = color_emoji * filled + "⬛" * (bar_length - filled)
    return f"{bar} **{int(percentage * 100)}%**"

# --- FUNCȚIE STACK LOGS ---
async def update_user_log(user, amount, boss_name):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    found_msg = None
    # Căutăm în ultimele 100 de mesaje din log-uri
    async for message in channel.history(limit=100):
        if message.author == bot.user and f"ID: {user.id}" in message.content:
            found_msg = message
            break

    if found_msg:
        # Extragem suma veche folosind regex
        match = re.search(r"Suma Totală: \*\*(\d+)\*\*", found_msg.content)
        if match:
            old_total = int(match.group(1))
            new_total = old_total + amount
            
            # Actualizăm mesajul existent
            new_content = (
                f"📊 **BAZĂ DE DATE VENUS2**\n"
                f"👤 **Jucător:** {user.mention} | (ID: {user.id})\n"
                f"💰 **Suma Totală:** **{new_total}** DC\n"
                f"⚔️ **Ultima pradă:** +{amount} DC de la {boss_name}\n"
                f"📅 *Ultima actualizare: <t:{int(discord.utils.utcnow().timestamp())}:R>*"
            )
            await found_msg.edit(content=new_content)
    else:
        # Dacă nu am găsit mesaj, creăm unul nou
        first_content = (
            f"📊 **BAZĂ DE DATE VENUS2**\n"
            f"👤 **Jucător:** {user.mention} | (ID: {user.id})\n"
            f"💰 **Suma Totală:** **{amount}** DC\n"
            f"⚔️ **Ultima pradă:** +{amount} DC de la {boss_name}\n"
            f"📅 *Înregistrare creată: <t:{int(discord.utils.utcnow().timestamp())}:R>*"
        )
        await channel.send(content=first_content)

# --- CLASA PENTRU LUPTĂ CO-OP ---
class BossCoopView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info = boss_info
        self.max_hp = 200 
        self.current_hp = 200
        self.damage_per_hit = 50
        self.participants = [] 

    @discord.ui.button(label="Atacă Bestia", style=discord.ButtonStyle.danger, custom_id="ataca_boss", emoji="⚔️")
    async def ataca_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        if user not in self.participants:
            if len(self.participants) >= 2:
                return await interaction.response.send_message("❌ Sălașul este plin!", ephemeral=True)
            self.participants.append(user)

        self.current_hp -= self.damage_per_hit

        if self.current_hp > 0:
            embed = discord.Embed(
                title=f"⚔️ Conflict: {self.boss_info['nume']}",
                description=(
                    f"🛡️ **Luptători:** {', '.join([u.mention for u in self.participants])}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"**ENERGIA BESTIEI:**\n{create_hp_bar(self.current_hp, self.max_hp)}\n"
                    f"━━━━━━━━━━━━━━━━━━"
                ),
                color=0x2ECC71
            )
            embed.set_image(url=self.boss_info['viu'])
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        
        else:
            button.disabled = True
            button.label = "Răpus!"
            button.style = discord.ButtonStyle.secondary

            drop_occurs = random.choices([True, False], weights=[25, 75], k=1)[0]
            
            embed_dead = discord.Embed(
                title=f"🏆 Triumf asupra lui {self.boss_info['nume']}!",
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
                    
                    # ACTUALIZARE STACKABLE LOG
                    await update_user_log(p, share, self.boss_info['nume'])
                
                embed_dead.description = (
                    f"Bestia a căzut!\n\n"
                    f"**PRADĂ OBȚINUTĂ:**\n{results_text}\n"
                    f"📜 *Baza de date a fost actualizată.*"
                )
            else:
                embed_dead.description = f"Bestia a murit, dar prada s-a irosit...\n\n**Pradă:** ❌ Niciun obiect valoros."

            embed_dead.set_footer(text="Venus2 - Battle System")
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
        title=f"👹 APARIȚIE: {boss_ales['nume']}",
        description=f"Se pot înscrie **2 războinici**.\n\n**ENERGIE:** {create_hp_bar(200, 200)}",
        color=0x2ECC71
    )
    embed.set_image(url=boss_ales['viu'])
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
