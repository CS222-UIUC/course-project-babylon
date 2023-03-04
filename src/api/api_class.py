import os
import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from math import floor
from bot import bot_class

class Event:
    """ 
    --Tass created Feb 15 2023--
    last update March 3 2023
    
    A class used to 
    - dump timestamp from trading book
    - help frontend recieve bot ececution records, graph, and related information.
    
    """
    def __init__(self):
        self._HIST_PATH = None
    
    def dump_history(self, timestamp):
        return
           
    def display_model():
        return
        
    def get_book():
        return
    
    def print_latest_order():
        return
        
    def print_all_orders():
        return
        
    def update_model():
        return
        
    def update_book():
        return
        
        

class Execution:
    """ 
    --Tass created Feb 15 2023--
    
    A class used to 
    - add, delete crypto symbols that bot control
    - start, pause the bot
    
    """
    def __init__(self):
        self._SYMBOLS = []
        self._BOTS = {}
        self.bot = None
        self._API_KEY = None
        self._SECRET = None
        self.BASE_URL = 'https://paper-api.alpaca.markets'
        self.trading_client = None
        self.account = None
        self.cash_to_spend = 0;
    
    def login(self, api, secret):
        self._API_KEY = api
        self._SECRET = secret
        self.set_client()
        self.set_account()
        print("LOGIN SUCCEED!")
        
    def create_bot(self, symbol, timeframe='5Min', rsi_period=14,rsi_upper=70,rsi_lower=30):
        self.BOTS[symbol] = bot_class.BOT (
            api = self.trading_client,
            symbol=symbol,
            timeframe=timeframe,
            rsi_period=rsi_period,
            rsi_upper=rsi_upper,
            rsi_lower=rsi_lower
        )
        
        
        
    def set_account(self):
        if self.trading_client != None:
            self.account = self.trading_client.get_account()
        else:
            print("set_account: NO CLIENT FOUND")
    
    def set_client(self):
        if self._API_KEY != None and self._SECRET!= None:
            #self.trading_client = TradingClient('api-key', 'secret-key', paper=True)
            self.trading_client = tradeapi.REST(key_id= self._API_KEY, secret_key=self._SECRET, base_url=self.BASE_URL)
            print("set_client: SUCCEED")
        else:
            print("set_client: KEYS INVALID")
    
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
        if self._API_KEY==None or self._SECRET==None:
            print("[set_user_info]: KEY INVALID")
        return self.account
    
    def set_user_info(self, new_key, new_secret):
        self._API_KEY = new_key
        self._SECRET = new_secret
    
    def clear_user_info(self):
        self._API_KEY = None
        self._SECRET = None
    
    def test_print(self):
        return "i can print!"
        
    
    