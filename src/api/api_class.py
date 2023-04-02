import os
import alpaca_trade_api as tradeapi
import yfinance as yf
from math import floor

# from srcbot import bot_class
import streamlit as st
from src.bot.bot_class import BOT, logs
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from datetime import timezone, datetime, timedelta
# logs = bot_class.logs
import pandas as pd


def LOGIN(key, secret):
    url = "https://paper-api.alpaca.markets"
    try:
        client_api = tradeapi.REST(key_id=key, secret_key=secret, base_url=url)
        client_api.get_account()
        return client_api
    except Exception as e:
        return -1


def LOGOUT():
    return None, None, None, None


class Execution:
    """
    --Tass created Feb 15 2023--
    last update March 15 2023

    A class used to
    - add, delete crypto symbols that bot control
    - start, pause the bot

    """

    def __init__(self, CLIENT_API):
        self._SYMBOLS = []
        self._BOTS = {}
        self.bot = None
        self.account = CLIENT_API.get_account()
        self.cash_to_spend = 0
        self.api = CLIENT_API

    def create_bot(
            self, symbol, timeframe="5Min", rsi_period=14, rsi_upper=70, rsi_lower=30
    ):
        self._BOTS[symbol] = BOT(
            api=self.api,
            symbol=symbol,
            timeframe=timeframe,
            rsi_period=rsi_period,
            rsi_upper=rsi_upper,
            rsi_lower=rsi_lower,
        )

    def set_account(self):
        if self.api != None:
            self.account = self.api.get_account()
        else:
            print("set_account: NO CLIENT FOUND")

    def get_account_cash(self):
        return float(self.account.cash)

    def set_cash_to_spend(self, percent):
        if percent >= 1:
            print("[set_cash_to_spend]: INVALID PERCENT")
            return
        self.cash_to_spend = float(self.account.cash) * percent

    def add_symbol(self, symbol: str):
        valid_symbol = self.check_symbol(symbol)

        if valid_symbol is -1:
            return False
        self._SYMBOLS.append(valid_symbol)
        self._BOTS[valid_symbol] = None  # unset
        return True

    def get_symbols(self):
        return self._SYMBOLS

    def check_symbol(self, symbol: str):
        import requests
        if not symbol.replace(" ", "").isalnum():
            print("[INVALID SYMBOL] ", symbol)
            return -1
        # Valid, uniform format
        valid_symbol = symbol.replace(" ", "").upper()
        try:
            stock_info = yf.Ticker(valid_symbol).info["symbol"]
            return valid_symbol
        except:
            return -1

    def delete_symbol(self, symbol: str):
        valid_symbol = self.check_symbol(symbol)
        if valid_symbol not in self._SYMBOLS:
            print("[Symbol not found]")
            return False
        self._SYMBOLS.remove(valid_symbol)
        del self._BOTS[valid_symbol]
        return True

    def start_bot(self, symbol):
        if self._BOTS[symbol] is None:
            print("BOT not created")
            return
        self._BOTS[symbol].paused = False

    def pause_bot(self, symbol):
        if self._BOTS[symbol] is None:
            print("BOT not created")
            return
        self._BOTS[symbol].pause()

    def reset_bot(self, symbol):
        self._BOTS[symbol] = -1

    def start_all_bots(self):
        for bot in self._BOTS:
            self.start_bot(bot)

    def pause_all_bots(self):
        for bot in self._BOTS:
            self.pause_bot(bot)

    def reset_all_bots(self):
        for bot in self._BOTS:
            self.reset_bot(bot)

    def get_user_info(self):
        return self.account

    def test_print(self):
        return "i can print!"


class Events:
    """
    --Tass created Feb 15 2023--
    last update March 10 2023

    A class used to
    - dump logs from csv file
    - help frontend recieve bot ececution records, graph, and related information.

    """

    def __init__(self, symbol):
        self.filtered_logs = [log_entry for log_entry in logs if log_entry[1] == symbol]
        self.SYMBOL = symbol

    def display_graph(self):
        return 0

    def show_logs(self):
        logs_text = ""
        for log_entry in self.filtered_logs[::-1]:
            # Add each log entry to the beginning of the log text
            logs_text = (
                    f"{log_entry[0]} {log_entry[1]} {log_entry[2]} {log_entry[3]} {log_entry[4]}\n"
                    + logs_text
            )
        # Display the logs in a reactive text area component
        st.text_area(f"Logs for {self.SYMBOL}", value=logs_text, key=self.SYMBOL)

    @staticmethod
    def delete_logs(self):  # permanently delete logs records
        logs.clear()
        return 0

        ## for frontend
        # def display_log_titles(self):
        #     st.title("Trade logs")
        #     st.subheader(self.SYMBOL)
        #     show_logs(self.SYMBOL)
        #     st.subheader(self.SYMBOL)
        #     show_logs(self.SYMBOL)
