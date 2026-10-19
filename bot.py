import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from commands import RiotCommands
from task import RiotTasks
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    RiotTasks(bot)
    print(f"Connecté en tant que {bot.user}")

async def main():
    await bot.add_cog(RiotCommands(bot))
    await bot.start(DISCORD_TOKEN)
    
asyncio.run(main())