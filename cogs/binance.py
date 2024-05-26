import os

import requests
from binance.spot import Spot
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
client = Spot()


class Binance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = 'https://api.binance.com/api/v3'
        self.client = Spot(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_SECRET_KEY'))

    @commands.command(aliases=["현물 가격", "현물"])
    async def spot_avg_price(self, ctx, symbol='BTCUSDT'):
        print('btc_spot_avg called')
        avg_price = self.client.avg_price(symbol)
        price = avg_price['price']
        minitues = avg_price['mins']
        await ctx.send(f'{minitues}분 동안의 {symbol} 평균 가격은 {price}$입니다.')

    @commands.command()
    async def btc(self, ctx):
        await ctx.send('BTC is a cryptocurrency.')


def setup(bot):
    bot.add_cog(Binance(bot))
