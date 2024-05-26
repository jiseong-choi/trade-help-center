import hashlib
import hmac
import logging
import os
import time
import win32api
from datetime import datetime

import requests as rq
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.spot import Spot
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Binance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = 'https://api.binance.com/api/v3'
        self.furl = 'https://fapi.binance.com'
        self.client = Spot(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_API_SECRET'))
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_API_SECRET')
        self.headers = {'X-MBX-APIKEY': self.api_key}

    def get_user_data(self, url_sub):
        now = rq.get(f'{self.url}/time').json()['serverTime']
        message = f'timestamp={now}'
        signature = hmac.new(key=self.secret_key.encode('utf-8'), msg=message.encode('utf-8'),
                             digestmod=hashlib.sha256).hexdigest()
        url = f'{self.furl}{url_sub}?{message}&signature={signature}'
        result = rq.get(url, headers=self.headers)
        return result.json()

    @commands.command(aliases=["현물가격", "현물"])
    async def spot_avg_price(self, ctx, symbol='BTCUSDT'):
        print('btc_spot_avg called')
        avg_price = self.client.avg_price(symbol)
        price = avg_price['price']
        minutes = avg_price['mins']
        await ctx.send(f'{minutes}분 동안의 {symbol} 평균 가격은 {price}$입니다.')

    @commands.command(aliases=["현재가격", "가격"])
    async def current_price(self, ctx, symbol='BTCUSDT'):
        print('current_price called')
        try:
            current_price = self.client.ticker_price(symbol)
            price = current_price['price']
            await ctx.send(f'{symbol}의 현재 가격은 {price}$입니다.')
        except BinanceAPIException as e:
            print(e)
            logging.error(e)
            await ctx.send('현재 가격을 가져오는 중 오류가 발생했습니다.')

    @commands.command(aliases=["잔고"])
    async def balance(self, ctx):
        print('balance called')
        try:
            balance = self.get_user_data('/fapi/v2/balance')
            # 잔고가 0이 아닌 자산만 필터링
            non_zero_balance = [asset for asset in balance if float(asset['balance']) > 0]
            balance_summary = [f"{asset['asset']}: {asset['balance']}" for asset in non_zero_balance]
            summary = "\n".join(balance_summary)
            if len(summary) > 2000:
                summary = summary[:1997] + '...'
            await ctx.send(f'계좌 잔고:\n{summary}')
        except Exception as e:
            print(e)
            logging.error(e)
            await ctx.send('잔고를 가져오는 중 오류가 발생했습니다.')

    @commands.command(aliases=["주문내역"])
    async def order_log(self, ctx):
        print('order_log called')
        try:
            order_log = self.get_user_data('/fapi/v1/allOrders')
            await ctx.send(f'주문 내역: {order_log}')
        except Exception as e:
            print(e)
            logging.error(e)
            await ctx.send('주문 내역을 가져오는 중 오류가 발생했습니다.')

    @commands.command(aliases=["계좌정보"])
    async def account(self, ctx):
        print('account called')
        try:
            account_info = self.get_user_data('/fapi/v2/account')

            # 잔고가 0이 아닌 자산 필터링
            non_zero_assets = [asset for asset in account_info['assets'] if float(asset['walletBalance']) > 0]
            assets_summary = [f"Asset: {asset['asset']}, Wallet Balance: {asset['walletBalance']}" for asset in
                              non_zero_assets]

            # 포지션이 0이 아닌 포지션 필터링
            non_zero_positions = [position for position in account_info['positions'] if
                                  float(position['positionAmt']) != 0]
            positions_summary = [f"Symbol: {position['symbol']}, Position: {position['positionAmt']}" for position in
                                 non_zero_positions]

            summary = "\n".join(assets_summary + positions_summary)

            # 메시지를 나누어 전송
            max_length = 2000
            for i in range(0, len(summary), max_length):
                await ctx.send(summary[i:i + max_length])

        except Exception as e:
            print(e)
            logging.error(e)
            await ctx.send('계좌 정보를 가져오는 중 오류가 발생했습니다.')

    @commands.command()
    async def test(self, ctx):
        print('test called')
        try:
            client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
            server_time = client.get_server_time()

            gmtime = time.gmtime(int((server_time["serverTime"]) / 1000))
            win32api.SetSystemTime(gmtime[0],
                                   gmtime[1],
                                   0,
                                   gmtime[2],
                                   gmtime[3],
                                   gmtime[4],
                                   gmtime[5],
                                   0)

            print(server_time)
            print(client.account())
        except BinanceAPIException as e:
            print(e)
            logging.error(e)
            await ctx.send('테스트 명령어 실행 중 오류가 발생했습니다.')


def setup(bot):
    bot.add_cog(Binance(bot))
