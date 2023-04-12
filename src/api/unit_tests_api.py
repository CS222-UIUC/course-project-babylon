# import sys
# sys.path.append("..")
import unittest
from api_class import *
import warnings

"""
TASS ONLY API TEST KEY
"""
API_KEY = "PKOQNDVM0R6J9YYPK1WW"  # fill by yourself, don't push to git
SECRET_KEY = "n02lBPUmKHqz77QwjscHfgrWUoNz9CBWwFMnqS4B"

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

    def test_invalid_credentials(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            # Set invalid API key and secret key
            invalid_api_key = "invalid_api_key"
            invalid_secret_key = "invalid_secret_key"

            # Call the LOGIN function with invalid credentials
            result = LOGIN(invalid_api_key, invalid_secret_key)

            # Check if the result is -1
            self.assertEqual(result, -1)

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

    def test_check_symbol_market(self):
        user = Execution(CLIENT_API)
        a1 = user.check_symbol("AAPL")
        self.assertEqual("AAPL",a1)
        a3 = user.check_symbol("TSLA")
        self.assertEqual("TSLA", a3)
        a4 = user.check_symbol("asdasd")
        self.assertEqual(-1, a4)
        a5 = user.check_symbol("BCCBCD")
        self.assertEqual(-1, a5)





if __name__ == "__main__":
    unittest.main()
