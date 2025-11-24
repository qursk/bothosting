import os
import discord
from discord.ext import commands
import webserver
# Allowed guild (server) ID
ALLOWED_GUILD_ID = 1436101095276675174

# Intents are required for certain events and functionalities
intents = discord.Intents.default()
intents.message_content = True  # Enable if you want to read message content

# Create bot instance with command prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})")

# Decorator to block commands on other servers
def guild_only(ctx):
    return ctx.guild and ctx.guild.id == ALLOWED_GUILD_ID

@bot.command(name="hello")
@commands.check(guild_only)
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! I'm your bot running on **your server**.")

@hello.error
async def hello_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return  # Ignoriert, falls Command auf einem anderen Server ausgeführt wird

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set")
    else:
        bot.run(TOKEN)
    

webserver.keep_alive()
