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
import pandas as pd
from datetime import date, datetime
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from alpaca_trade_api.rest import REST, TimeFrame
import json
import backtrader as bt
import backtrader.feeds as btfeeds

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

trading_pair = "BTCUSD"
exchange = "FTXU"
one_year_ago = datetime.now() - relativedelta(years=1)
start_date = str(one_year_ago.date())
today = date.today()
today = today.strftime("%Y-%m-%d")
rsi_upper_bound = 70
rsi_lower_bound = 30
bollinger_window = 20
waitTime = 3600  # Wait time between each bar request -> 1 hour (3600 seconds)
percent_trade = 0.2
bar_data = 0
latest_bar_data = 0
btc_position = 0
usd_position = 0

# Alpaca API
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_DATA_URL = "https://data.alpaca.markets"

HEADERS = {
    "APCA-API-KEY-ID": config.APCA_API_KEY_ID,
    "APCA-API-SECRET-KEY": config.APCA_API_SECRET_KEY,
}

# Alpaca client
client = REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY)


def calculate_order_size(cash_to_spend, latest_price):
    precision_factor = 10000
    units_to_buy = np.floor(cash_to_spend * precision_factor / latest_price)
    units_to_buy /= precision_factor
    return units_to_buy


def get_bb(df):
    # calculate bollinger bands
    indicator_bb = BollingerBands(
        close=df["close"], window=bollinger_window, window_dev=2
    )
    # Add Bollinger Bands to the dataframe
    df["bb_mavg"] = indicator_bb.bollinger_mavg()
    df["bb_upper"] = indicator_bb.bollinger_hband()
    df["bb_lower"] = indicator_bb.bollinger_lband()

    # Add Bollinger Band high indicator
    df["bb_hi"] = indicator_bb.bollinger_hband_indicator()
    # Add Bollinger Band low indicator
    df["bb_li"] = indicator_bb.bollinger_lband_indicator()
    return df


def get_rsi(df):
    indicator_rsi = RSIIndicator(close=df["close"], window=14)
    df["rsi"] = indicator_rsi.rsi()
    return df


def get_positions():
    """
    Get positions on Alpaca
    """
    try:
        positions = requests.get(
            "{0}/v2/positions".format(ALPACA_BASE_URL), headers=HEADERS
        )
        logger.info(
            "Alpaca positions reply status code: {0}".format(positions.status_code)
        )
        if positions.status_code != 200:
            logger.info("Undesirable response from Alpaca! {}".format(positions.json()))
        if len(positions.json()) != 0:
            btc_position = positions.json()[0]["qty"]
        else:
            btc_position = 0
        logger.info("BTC Position on Alpaca: {0}".format(btc_position))
    except Exception as e:
        logger.exception(
            "There was an issue getting positions from Alpaca: {0}".format(e)
        )
    return btc_position


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
