import unittest
from bot_class import *

"""
TASS ONLY API TEST KEY
"""
API_KEY = "PK32AI2DQDHK074B5IMR"
SECRET_KEY = "MwoUg7Q9cjDoh8cbTnbQrAXV8rJh7cQYpZ9vCQin"
BASE_URL = "https://paper-api.alpaca.markets"

CLIENT_API = tradeapi.REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url=BASE_URL)


class Test_BOT_CLASS(unittest.TestCase):
    """ 
    --Tass created Mar 7 2023--
    last update March 7 2023
    
    A class used to test
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
        self.assertEqual(position[2], "open")
        self.assertEqual(position[3], "buy")
        self.assertEqual(position[4], 1)

        print("Open long positon executed, sleep 10 secs")
        time.sleep(10)  # sleep 10 secs to check on Alpaca

        order = position[1]
        AAPL.cancel_position(order.id)  # then cancel it
        print("Cancel long positon order executed")

        short_position = AAPL.open_position(0, 2)  # buy 2
        self.assertEqual(short_position[2], "open")
        self.assertEqual(short_position[3], "sell")
        self.assertEqual(short_position[4], 2)
        order = short_position[1]
        print("Open short positon executed, sleep 10 secs")
        time.sleep(10)  # sleep 10 secs to check on Alpaca
        AAPL.cancel_position(order.id)  # then cancel it
        print("Cancel short positon order executed")

    def test_close_position(self):
        AAPL = BOT(
            api=CLIENT_API,
            symbol="AAPL",
            timeframe="5Min",
            rsi_period=14,
            rsi_upper=70,
            rsi_lower=30,
        )
        position = AAPL.open_position(1, 2)  # buy 2
        order = position[1]
        print("Open long positon executed, sleep 20 secs")
        time.sleep(20)

        print("Start executing close long positon")
        AAPL.close_position(order.id, 0.5)  # close half position
        print("Close long positon executed, sleep 10 secs")
        time.sleep(10)  # sleep 10 secs to check on Alpaca


if __name__ == "__main__":
    unittest.main()
