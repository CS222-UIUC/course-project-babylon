import unittest
from bot_class import *

"""
TASS ONLY API TEST KEY
"""
API_KEY = None  # fill by yourself, don't push to git
SECRET_KEY = None
BASE_URL = "https://paper-api.alpaca.markets"

CLIENT_API = tradeapi.REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url=BASE_URL)


class Test_BOT_CLASS(unittest.TestCase):
    """
    --Tass created Mar 7 2023--
    last update April 5 2023

    A class used to testﬁ
    - start/pause/reset of the bot
    - open/close/decline order
    - stability of Alpaca API
    - basic index trading strategy

    """

    def test_open_position(self):  # cancel positon also tested
        AAPL = BOT(
            api=CLIENT_API,
            symbol="AAPL",
            timeframe="5Min",
            rsi_period=14,
            rsi_upper=70,
            rsi_lower=30,
        )
        position = AAPL.open_position(1, 1)  # buy 1

        print("Open long positon executed, sleep 10 secs")
        time.sleep(10)  # sleep 10 secs to check on Alpaca

        short_position = AAPL.open_position(0, 2)  # sell 2

        print("Open short positon executed, sleep 10 secs")
        time.sleep(10)  # sleep 10 secs to check on Alpaca
        AAPL.close_short_position()  # then cancel it
        print("Close short positon order executed")

    def test_close_position(self):
        AAPL = BOT(
            api=CLIENT_API,
            symbol="AAPL",
            timeframe="5Min",
            rsi_period=14,
            rsi_upper=70,
            rsi_lower=30,
        )
        position = AAPL.open_position(0, 2)  # sell 2
        print("Open long positon executed, sleep 10 secs")
        time.sleep(10)

        print("Start executing close long positon")
        AAPL.close_short_position()  # close half position
        print("Close long positon executed, sleep 10 secs")
        time.sleep(10)  # sleep 10 secs to check on Alpaca




    def test_run_strategy(self):
        AAPL = BOT(
            api=CLIENT_API,
            symbol="AAPL",
            timeframe="5Min",
            rsi_period=14,
            rsi_upper=70,
            rsi_lower=30,
        )

        AAPL.start()
        time.sleep(10)  # sleep 10 secs to check on Alpaca
        AAPL.pause()





if __name__ == "__main__":
    unittest.main()
