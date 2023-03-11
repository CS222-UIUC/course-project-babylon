import os
import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from math import floor
from bot import bot_class
import pandas as pd

df = pd.read_csv("logs_database.csv")

API_KEY, SECRET_KEY, BASE_URL,CLIENT_API = None

def LOGIN(key, secret):
    url = 'https://paper-api.alpaca.markets'
    return key, secret, url,tradeapi.REST(key_id= key, secret_key=secret, base_url=url)
    
def LOGOUT(self):
    return None,None,None,None



class Execution:
    """ 
    --Tass created Feb 15 2023--
    last update March 10 2023
    
    A class used to 
    - add, delete crypto symbols that bot control
    - start, pause the bot
    
    """
    def __init__(self):
        self._SYMBOLS = []
        self._BOTS = {}
        self.bot = None
        self.account = None
        self.cash_to_spend = 0;
    
        
    def create_bot(self, symbol, timeframe='5Min', rsi_period=14,rsi_upper=70,rsi_lower=30):
        self.BOTS[symbol] = bot_class.BOT (
            api = CLIENT_API,
            symbol=symbol,
            timeframe=timeframe,
            rsi_period=rsi_period,
            rsi_upper=rsi_upper,
            rsi_lower=rsi_lower
        )
        
        
    def set_account(self):
        if CLIENT_API != None:
            self.account = CLIENT_API.get_account()
        else:
            print("set_account: NO CLIENT FOUND")
    
    
    def get_account_cash(self):
        return float(self.account.cash)
    
    def set_cash_to_spend(self, percent):
        if percent >= 1:
            print("[set_cash_to_spend]: INVALID PERCENT")
            return
        self.cash_to_spend = float(self.account.cash) * percent;
        
    def add_symbol(self, symbol:str):
        valid_symbol = self.check_symbol(symbol)
        if valid_symbol==None:
            return None
        self._SYMBOLS.append(valid_symbol)
        self._BOTS[valid_symbol] = None #unset
        
    def get_symbols(self):
        return self._SYMBOLS
    
    def check_symbol(self, symbol: str) ->str:
        if not symbol.replace(" ", "").isalnum(): 
            print("[INVALID SYMBOL] ", symbol)
            return None
        
        # Valid, uniform format
        valid_symbol = symbol.replace(" ", "").upper()
        return valid_symbol
        
    
    def delete_symbol(self, symbol:str):
        valid_symbol = self.check_symbol(symbol)
        if valid_symbol not in self._SYMBOLS: 
            print("[Symbol not found]")
            return None
        self._SYMBOLS.remove(valid_symbol)
        del self._BOTS[valid_symbol]
    
    def start_bot(self, symbol):
        self._BOTS[symbol].start()
    
    def pause_bot(self, symbol):
        self._BOTS[symbol].pause()
        
    def reset_bot(self, symbol):
        self._BOTS[symbol] = -1
        
    def start_all_bots(self):
        for bot in self._BOTS: self.start_bot(bot)
    
    def pause_all_bots(self):
        for bot in self._BOTS: self.pause_bot(bot)
        
    def reset_all_bots(self):
        for bot in self._BOTS: self.reset_bot(bot)
        
    def get_user_info(self):
        if API_KEY==None or SECRET_KEY==None:
            print("[set_user_info]: KEY INVALID")
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
        self.DATABASE = df[df["Symbol"]]
        self.SYMBOL = symbol
        
    def display_graph(self):
        
    
    def dump_latest_logs(self, qty):
        
           
    def delete_logs(self): #permanently delete logs records
        
        
        

        