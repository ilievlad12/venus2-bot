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
    return "Venus2 Bot: Sistemul Co-op este Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- CONFIGURARE BOSI ---
BOSI_DATA = [
    {"nume": "Căpitanul Bestie", "viu": "https://i.imgur.com/XgL4k0U.png", "mort": "https://i.imgur.com/cLaeG60.jpeg"},
    {"nume": "Chuong", "viu": "https://i.imgur.com/FFqWaMV.png", "mort": "https://i.imgur.com/3bfJjYh.jpeg"},
    {"nume": "Goo-Pae", "viu": "https://i.imgur.com/wDynbzc.png", "mort": "https://i.imgur.com/Vp8Gq3B.jpeg"},
    {"nume": "Mahon", "viu": "https://i.imgur.com/uxR8aXP.png", "mort": "https://i.imgur.com/6rhZfxt.jpeg"}
]

def create_hp_bar(current, maximum):
    percentage = max(0, min(current / maximum, 1))
    bar_length = 10
    filled = int(percentage * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    return f"`[{bar}]` {int(percentage * 100)}%"

# --- CLASA PENTRU LUPTĂ CO-OP ---
class BossCoopView(discord.ui.View):
    def __init__(self, boss_info):
        super().__init__(timeout=None)
        self.boss_info = boss_info
        self.max_hp = 100
        self.current_hp = 100
        self.damage_per_hit = 50
        self.participants = [] # Lista cu userii care au dat hit

    @discord.ui.button(label="Atacă Boss-ul", style=discord.ButtonStyle.danger, custom_id="ataca_boss", emoji="⚔️")
    async def ataca_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # Verificăm dacă sunt deja 2 participanți și dacă userul actual este unul dintre ei
        if user not in self.participants:
            if len(self.participants) >= 2:
                return await interaction.response.send_message("❌ Această luptă este deja plină! Doar 2 eroi se pot bate cu acest boss.", ephemeral=True)
            self.participants.append(user)

        self.current_hp -= self.damage_per_hit

        # Boss-ul încă trăiește
        if self.current_hp > 0:
            embed = discord.Embed(
                title=f"⚔️ Luptă în echipă: {self.boss_info['nume']}",
                description=(
                    f"Eroii participanți: {', '.join([u.mention for u in self.participants])}\n\n"
                    f"**HP Rămas:**\n{create_hp_bar(self.current_hp, self.max_hp)}\n\n"
                    f"💥 {user.mention} a lovit cu **-50 HP**!"
                ),
                color=0xFF4500
            )
            embed.set_image(url=self.boss_info['viu'])
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        
        # Boss-ul a murit
        else:
            button.disabled = True
            button.label = "Doborât!"
            button.style = discord.ButtonStyle.secondary

            drop_occurs = random.choices([True, False], weights=[60, 40], k=1)[0]
            
            embed_dead = discord.Embed(
                title=f"🏆 {self.boss_info['nume']} a fost învins în echipă!",
                color=0x2ECC71
            )
            embed_dead.set_image(url=self.boss_info['mort'])
            embed_dead.set_thumbnail(url=bot.user.display_avatar.url)

            if drop_occurs:
                results_text = ""
                for p in self.participants:
                    # Verificare tag pentru fiecare participant în parte
                    has_tag = "[Venus2]" in p.display_name or any(role.name == "Venus2" for role in p.roles)
                    share = 150 if has_tag else 50
                    tag_status = "✨ (VIP)" if has_tag else ""
                    results_text += f"👤 {p.mention} ➔ **{share} DC** {tag_status}\n"
                
                embed_dead.description = (
                    f"Eroii care au împărțit prada:\n\n{results_text}\n"
                    f"Felicitări pentru colaborare!"
                )
            else:
                embed_dead.description = (
                    f"Eroii {', '.join([u.mention for u in self.participants])} au ucis boss-ul,\n"
                    f"dar acesta nu a lăsat niciun drop în urmă.\n\n"
                    f"**Drop:** ❌ Nimic"
                )

            info_text = (
                "🪙 **50 DC** ➔ Cotă Standard (per om)\n"
                "💎 **150 DC** ➔ Cotă VIP (per om)\n\n"
                "💡 **Sfat:** Ambii eroi trebuie să poarte tag-ul **[Venus2]** pentru cota maximă!"
            )
            embed_dead.add_field(name="📦 Detalii Împărțire", value=info_text, inline=False)
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
        title=f"⚠️ BOSS: {boss_ales['nume']}",
        description=(
            f"Un boss a apărut! Se pot înscrie **maxim 2 jucători**.\n\n"
            f"**HP:** {create_hp_bar(100, 100)}\n"
            "Fiecare lovitură scade **50 HP**."
        ),
        color=0xFF4500
    )
    embed.set_image(url=boss_ales['viu'])
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    await ctx.send(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
