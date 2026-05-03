import os
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
    return "Venus2 Bot este Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def metin(ctx):
    has_tag = "[Venus2]" in ctx.author.display_name or any(role.name == "Venus2" for role in ctx.author.roles)
    dc_amount = 300 if has_tag else 100
    drop_chance = random.randint(1, 100)

    embed = discord.Embed(
        title="☄️ Venus2 Metin Stone Destroyed",
        description=f"{ctx.author.mention} a distrus **Piatra Metin a Venerei**!",
        color=discord.Color.red()
    )

    if drop_chance <= 30:
        embed.add_field(name="💰 Drop Information", 
                        value=f"• 🪙 **{dc_amount} DC** {'(Bonus tag Venus2)' if has_tag else '(Fără tag)'}", 
                        inline=False)
    else:
        embed.add_field(name="❌ Drop Information", value="• ❌ **Nimic...**", inline=False)
        
    await ctx.send(embed=embed)

keep_alive()
# Luăm token-ul din setările Render, nu din cod!
bot.run(os.getenv('DISCORD_TOKEN'))
