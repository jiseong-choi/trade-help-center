import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from cogs.binance import Binance

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='>', intents=intents)


async def load_extensions():
    await bot.add_cog(Binance(bot))


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


async def main():
    async with bot:
        await load_extensions()
        print('Bot is ready!')
        await bot.start(TOKEN)

asyncio.run(main())