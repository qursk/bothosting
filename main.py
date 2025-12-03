# main.py
import os
from bot import MyBot
from roles import RolesCog
from weekly import WeeklyCog
from utils import load_json
from config import ROLES_FILE, WEEKLY_FILE
from webserver import keep_alive

bot = MyBot()


@bot.event
async def on_ready():
    print(f"Bot gestartet als {bot.user}")

    # Daten laden
    await bot.get_cog("RolesCog").load()
    await bot.get_cog("WeeklyCog").load()


keep_alive()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
