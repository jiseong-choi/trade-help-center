from discord.ext import commands


class Binance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def price(self, ctx, symbol: str):
        await ctx.send(f'{symbol}의 가격은 100원입니다.')

    @commands.command()
    async def test(self, ctx):
        await ctx.send('test')


def setup(bot):
    bot.add_cog(Binance(bot))
