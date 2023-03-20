import sys

sys.path.append("..")

import unittest
from src.api.api_class import *

"""
TASS ONLY API TEST KEY
"""
API_KEY = None  # fill by yourself, don't push to git
SECRET_KEY = None
CLIENT_API = LOGIN(API_KEY, SECRET_KEY)


class Test_API_CLASS(unittest.TestCase):
    def test_print(self):
        user = Execution(CLIENT_API)
        self.assertEqual(user.test_print(), "i can print!")

    def test_check_symbols(self):
        user = Execution(CLIENT_API)
        a1 = user.check_symbol("BTC USDT")
        a2 = user.check_symbol("btc eTh ")
        a3 = user.check_symbol("e t h s py")
        a4 = user.check_symbol("    ###")
        a5 = user.check_symbol(" BTCETH   ###")
        self.assertEqual(a1, "BTCUSDT")
        self.assertEqual(a2, "BTCETH")
        self.assertEqual(a3, "ETHSPY")
        self.assertEqual(a4, None)
        self.assertEqual(a5, None)

        # self.assertFalse('Foo'.isupper())

    def test_add_symbols(self):
        user = Execution(CLIENT_API)
        user.add_symbol("btc eth")
        user.add_symbol("SolonaUsdt")
        user.add_symbol("###")
        symbols = user.get_symbols()
        s = ["BTCETH", "SOLONAUSDT"]
        self.assertEqual(len(symbols), 2)
        for i in range(len(symbols)):
            self.assertEqual(symbols[i], s[i])

    def test_del_symbols(self):
        user = Execution(CLIENT_API)
        user.add_symbol("btc eth")
        user.add_symbol("SolonaUsdt")
        user.add_symbol("UST")
        user.delete_symbol("btceth")
        self.assertEqual(user.get_symbols(), ["SOLONAUSDT", "UST"])
        user.delete_symbol("btceth")
        self.assertEqual(user.get_symbols(), ["SOLONAUSDT", "UST"])
        user.delete_symbol("shhh")
        self.assertEqual(user.get_symbols(), ["SOLONAUSDT", "UST"])
        user.delete_symbol("UST")
        self.assertEqual(user.get_symbols(), ["SOLONAUSDT"])
        user.delete_symbol("SOLONAUSDT")
        self.assertEqual(user.get_symbols(), [])

    def test_login(self):
        user = Execution(CLIENT_API)
        self.assertEqual(user.get_account_cash(), 100000.0)

    def test_bot_status(self):
        user = Execution(CLIENT_API)
        user.add_symbol("USDT")
        user.create_bot("USDT")
        user.start_bot("USDT")
        self.assertEqual(user._BOTS["USDT"].paused, False)
        user.pause_bot("USDT")
        self.assertEqual(user._BOTS["USDT"].paused, True)
        user.reset_bot("USDT")
        self.assertEqual(user._BOTS["USDT"], -1)

    # def test_dump_log(self):
    #     user = Execution(CLIENT_API)
    #     user.add_symbol("USDT")
    #     user.create_bot("USDT")
    #     event = Events("USDT")
    #     log = event.dump_latest_logs()
    #     print("============")
    #     print(log)
    #     print("============")


if __name__ == "__main__":
    unittest.main()
