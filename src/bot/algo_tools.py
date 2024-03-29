""" 
--Tass created Feb 28 2023--
last update Feb 28 2023

A file used to
- algo helper functions
- set model parameters
- strategies (maybe)
"""

import numpy as np
from dateutil.relativedelta import relativedelta
import config
import logging
import asyncio
import requests
import sys
from datetime import date, datetime
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import json
import backtrader as bt
import backtrader.feeds as btfeeds

# handler = logging.FileHandler('app.log')
# # Configure the logging level and format
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
#
# # Add the file handler to the logger
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)
# # Redirect stdout and stderr to the logger
# sys.stdout = handler.stream
# sys.stderr = handler.stream
#
# trading_pair = "BTCUSD"
# exchange = "FTXU"
# one_year_ago = datetime.now() - relativedelta(years=1)
# start_date = str(one_year_ago.date())
# today = date.today()
# today = today.strftime("%Y-%m-%d")
# rsi_upper_bound = 70
# rsi_lower_bound = 30
# bollinger_window = 20
# waitTime = 3600  # Wait time between each bar request -> 1 hour (3600 seconds)
# percent_trade = 0.2
# bar_data = 0
# latest_bar_data = 0
# btc_position = 0
# usd_position = 0

# Alpaca API
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_DATA_URL = "https://data.alpaca.markets"

HEADERS = {
    "APCA-API-KEY-ID": config.APCA_API_KEY_ID,
    "APCA-API-SECRET-KEY": config.APCA_API_SECRET_KEY,
}

# Alpaca client
client = REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY)



# def get_account_details():
#     """
#     Get Alpaca Trading Account Details
#     """
#     try:
#         account = requests.get(
#             '{0}/v2/account'.format(ALPACA_BASE_URL), headers=HEADERS)
#         if account.status_code != 200:
#             logger.info(
#                 "Undesirable response from Alpaca! {}".format(account.json()))
#             return False
#     except Exception as e:
#         logger.exception(
#             "There was an issue getting account details from Alpaca: {0}".format(e))
#         return False
#     return account.json()


# async def get_crypto_bar_data(trading_pair, start_date, end_date, exchange):
#     """
#     Get bar data from Alpaca for a given trading pair and exchange
#     """
#     try:
#
#         bars = client.get_crypto_bars(
#             trading_pair, TimeFrame(1, TimeFrameUnit.Hour), start=start_date, end=end_date, limit=10000,
#             exchanges=exchange).df
#
#         bars = bars.drop(
#             columns=["trade_count", "exchange"], axis=1)
#
#         # Get RSI for the bar data
#         bars = get_rsi(bars)
#         # Get Bollinger Bands for the bar data
#         bars = get_bb(bars)
#         bars = bars.dropna()
#         bars['timestamp'] = bars.index
#
#         # Assigning bar data to global variables
#         global latest_bar_data
#         global bar_data
#         bar_data = bars
#         # The latest bar data is the last bar in the bar data
#         latest_bar_data = bars[-1:]
#     # If there is an error, log it
#     except Exception as e:
#         logger.exception(
#             "There was an issue getting trade quote from Alpaca: {0}".format(e))
#         return False
#
#     return bars


# async def check_condition():
#     logger.info("Checking BTC position on Alpaca")
#     global btc_position
#     btc_position = float(get_positions())
#     # Log the latest closing price, RSI, and Bollinger Bands
#     logger.info("Checking Buy/Sell conditions for Bollinger bands and RSI")
#     logger.info("Latest Closing Price: {0}".format(
#         latest_bar_data['close'].values[0]))
#     logger.info("Latest Upper BB Value: {0}".format(
#         latest_bar_data['bb_upper'].values[0]))
#     logger.info("Latest MAvg BB Value: {0}".format(
#         latest_bar_data['bb_mavg'].values[0]))
#     logger.info("Latest Lower BB Value: {0}".format(
#         latest_bar_data['bb_lower'].values[0]))
#     logger.info("Latest RSI Value: {0}".format(
#         latest_bar_data['rsi'].values[0]))
#
#     if latest_bar_data.empty:
#         logger.info("Unable to get latest bar data")
#     # If we have a position, bollinger high indicator is 1 and RSI is above the upperbound, then sell
#     if ((latest_bar_data['bb_hi'].values[0] == 1) & (latest_bar_data['rsi'].values[0] > rsi_upper_bound) & (
#             btc_position > 0)):
#         logger.info(
#             "Sell signal: Bollinger bands and RSI are above upper bound")
#         sell_order = await post_alpaca_order(trading_pair, btc_position, 'sell', 'market', 'gtc')
#         if sell_order['status'] == 'accepted':
#             logger.info("Sell order successfully placed for {0} {1}".format(
#                 btc_position, trading_pair))
#         elif (sell_order['status'] == 'pending_new'):
#             logger.info("Sell order is pending.")
#             logger.info("BTC Position on Alpaca: {0}".format(get_positions()))
#         else:
#             logger.info("Sell order status: {0}".format(sell_order))
#     # If we do not have a position, bollinger low indicator is 1 and RSI is below the lowerbound, then buy
#     elif ((latest_bar_data['bb_li'].values[0] == 1) & (latest_bar_data['rsi'].values[0] < rsi_lower_bound) & (
#             btc_position == 0)):
#         logger.info("Buy signal: Bollinger bands and RSI are below lower bound")
#         qty_to_buy = (percent_trade * usd_position) / latest_bar_data['close'].values[0]
#         buy_order = await post_alpaca_order(trading_pair, qty_to_buy, 'buy', 'market', 'gtc')
#         if buy_order['status'] == 'accepted':
#             logger.info("Buy order successfully placed for {0} {1}".format(
#                 qty_to_buy, trading_pair))
#         elif (buy_order['status'] == 'pending_new'):
#             logger.info("Buy order is pending.")
#             logger.info("BTC Position on Alpaca: {0}".format(get_positions()))
#         else:
#             logger.info("Buy order status: {0}".format(buy_order))
#     # If we do not meet the above conditions, then we hold till we analyze the next bar
#     else:
#         logger.info("Hold signal: Bollinger bands and RSI are within bounds")


# async def post_alpaca_order(symbol, qty, side, type, time_in_force):
#     """
#     Post an order to Alpaca
#     """
#     try:
#         order = requests.post(
#             '{0}/v2/orders'.format(ALPACA_BASE_URL), headers=HEADERS, json={
#                 'symbol': symbol,
#                 'qty': qty,
#                 'side': side,
#                 'type': type,
#                 'time_in_force': time_in_force,
#                 'client_order_id': 'bb_rsi_strategy'
#             })
#         logger.info('Alpaca order reply status code: {0}'.format(
#             order.status_code))
#         if order.status_code != 200:
#             logger.info(
#                 "Undesirable response from Alpaca! {}".format(order.json()))
#             return False
#     except Exception as e:
#         logger.exception(
#             "There was an issue posting order to Alpaca: {0}".format(e))
#         return False
#     return order.json()


async def main():
    '''
   Get historical data from Alpaca and calculate RSI and Bollinger Bands.
   Backtest historical data to determine buy/sell/hold decisions and test performance.
   After backtesting, plot the results. Then, enter the loop to wait for new data and
   calculate entry and exit decisions.
   '''
    # Log the current balance of the MATIC token in our Alpaca account
    logger.info('BTC Position on Alpaca: {0}'.format(get_positions()))
    # Log the current Cash Balance (USD) in our Alpaca account
    global usd_position
    usd_position = float(get_account_details()['cash'])
    logger.info("USD position on Alpaca: {0}".format(usd_position))
    # Get the historical data from Alpaca for backtesting
    await get_crypto_bar_data(trading_pair, start_date, today, exchange)
    # Add bar_data to a CSV for backtrader
    bar_data.to_csv('bar_data.csv', index=False)
    # Create and run a Backtest instance
    await backtest_returns()

    while True:
        l1 = loop.create_task(get_crypto_bar_data(
            trading_pair, start_date, today, exchange))
        # Wait for the tasks to finish
        await asyncio.wait([l1])
        # Check if any trading condition is met
        await check_condition()
        # Wait for the a certain amount of time between each bar request
        await asyncio.sleep(waitTime)


def calculate_order_size(cash_to_spend, latest_price):
    precision_factor = 10000
    units_to_buy = np.floor(cash_to_spend * precision_factor / latest_price)
    units_to_buy /= precision_factor
    return units_to_buy


# def get_bb(df):
#     # calculate bollinger bands
#     indicator_bb = BollingerBands(
#         close=df["close"], window=bollinger_window, window_dev=2
#     )
#     # Add Bollinger Bands to the dataframe
#     df["bb_mavg"] = indicator_bb.bollinger_mavg()
#     df["bb_upper"] = indicator_bb.bollinger_hband()
#     df["bb_lower"] = indicator_bb.bollinger_lband()
#
#     # Add Bollinger Band high indicator
#     df["bb_hi"] = indicator_bb.bollinger_hband_indicator()
#     # Add Bollinger Band low indicator
#     df["bb_li"] = indicator_bb.bollinger_lband_indicator()
#     return df
#
#
# def get_rsi(df):
#     indicator_rsi = RSIIndicator(close=df["close"], window=14)
#     df["rsi"] = indicator_rsi.rsi()
#     return df


# def get_positions():
#     """
#     Get positions on Alpaca
#     """
#     try:
#         positions = requests.get(
#             "{0}/v2/positions".format(ALPACA_BASE_URL), headers=HEADERS
#         )
#         logger.info(
#             "Alpaca positions reply status code: {0}".format(positions.status_code)
#         )
#         if positions.status_code != 200:
#             logger.info("Undesirable response from Alpaca! {}".format(positions.json()))
#         if len(positions.json()) != 0:
#             btc_position = positions.json()[0]["qty"]
#         else:
#             btc_position = 0
#         logger.info("BTC Position on Alpaca: {0}".format(btc_position))
#     except Exception as e:
#         logger.exception(
#             "There was an issue getting positions from Alpaca: {0}".format(e)
#         )
#     return btc_position


# double RSI Strtegies
# Daily above 60, current below 30, long when RSI close above 30, 1.5 risk reward ratio
# Daily RSI below 40, current rsi above 70, short when RSI close below 70

def double_rsi_strad(rsi: list):
    sections = []
    for i in range(len(rsi)):
        if rsi[i] < 30:
            section = 'oversold'
        elif rsi[i] > 70:
            section = 'overbought'
        else:
            section = None
        sections.append(section)


async def backtest_returns():
    cerebro = bt.Cerebro()
    data = btfeeds.GenericCSVData(
        dataname='bar_data.csv',

        fromdate=datetime(2021, 7, 9, 0, 0, 0, 0),
        todate=datetime(2022, 7, 8, 0, 0, 0, 0),

        nullvalue=0.0,

        dtformat=('%Y-%m-%d %H:%M:%S%z'),
        timeframe=bt.TimeFrame.Minutes,
        compression=60,
        datetime=12,
        high=1,
        low=2,
        open=0,
        close=3,
        volume=4,
        openinterest=-1,
        rsi=6,
        bb_hi=10,
        bb_li=11
    )
    cerebro.broker.set_cash(100000.0)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=20)
    cerebro.adddata(data)
    cerebro.addstrategy(BB_RSI_Strategy)
    print("Starting Portfolio Value: ${}".format(cerebro.broker.getvalue()))

    cerebro.run()

    print("Final Portfolio Value: ${}".format(cerebro.broker.getvalue()))

    cerebro.plot()

    return


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
