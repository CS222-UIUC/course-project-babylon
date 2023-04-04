import alpaca_trade_api as tradeapi
import time
import pandas as pd
import datetime as dt
import pytz
from alpaca_trade_api.rest import REST, TimeFrame
from pip._internal import main as install
install(["install","ta-lib"])
import talib
import logging

logs = []
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def configure_logging():
    # Configure the logging module
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    return logging.getLogger(__name__)


class BOT:
    """
    --Tass created Feb 16 2023--
    last update April, 2 2023

    A class used to
    - get trading bot information and working status
    - read data from Alpaca market
    - place, change, cancel orders

    """

    def __init__(self, api, symbol, timeframe, rsi_period, rsi_upper, rsi_lower):
        self.symbol = symbol
        self.timeframe = timeframe
        self.rsi_period = rsi_period
        self.rsi_upper = rsi_upper
        self.rsi_lower = rsi_lower
        self.api = api
        self.paused = False
        self.logger = configure_logging()

    def start(self):
        self.logger.info("=== Bot is started ===")
        while not self.paused:
            try:
                self.run_strategy()
            except Exception as e:
                self.logger.info(f"=== Error in strategy: {e} ===")
                time.sleep(60)

    def pause(self):
        self.logger.info("=== Bot is paused ===")
        self.paused = True

    def get_last14Days_bars(self):
        _timeNow = dt.datetime.now(pytz.timezone('US/Central'))
        _14DaysAgo = _timeNow - dt.timedelta(days=14)

        _bars = self.api.get_bars(self.symbol, TimeFrame.Day,
                                  start=_14DaysAgo.isoformat(),
                                  end=None,
                                  limit=14
                                  )
        return _bars

    def run_strategy(self):
        # Get historical price data
        # day_bars = self.api.get_barset(self.symbol, "day", limit=self.rsi_period)
        bars = self.get_last14Days_bars()
        prices = bars.df["close"]

        # Calculate RSI
        rsi = talib.RSI(prices, timeperiod=9)[-1]
        self.logger.info(f"=== Try to get last 9Days RSI: {rsi} ===")

        # Check if RSI is above upper threshold and open a short position
        if rsi > self.rsi_upper:
            if not self.has_short_position():
                self.open_position(0, 1)
        # Check if RSI is below lower threshold and close the short position
        elif rsi < self.rsi_lower or rsi < 60:
            if self.has_short_position():
                self.close_short_position()

    def has_short_position(self):
        # Check if there is an open short position for the symbol
        positions = self.api.list_positions()
        for position in positions:
            if position.symbol == self.symbol and position.side == "short":
                self.logger.info("Short Position Detected")
                return True
        self.logger.info("Short Position Not Detected")
        return False

    def open_position(self, dir, qty):  # 1 is long, 0 is short
        # Place a short sell order for the symbol
        if dir == 1:
            side = "buy"
        else:
            side = "sell"
        order = self.api.submit_order(
            symbol=self.symbol, qty=qty, side=side, type="market", time_in_force="gtc"
        )
        executed_at = order.submitted_at
        self.logger.info(f"Opened position with order ID {order.id} at {executed_at}")
        self.logger.info(f"Side: {side} Qty: {qty}")
        # update_log(executed_at, self.symbol, order.id, side, qty)
        return 1

    def close_position(self, order_id, percent):
        position = self.api.get_position(self.symbol)
        qty = abs(int(float(position.qty)))
        side = "buy" if position.side == "short" else "sell"
        # Calculate the quantity to close based on the specified percentage
        close_qty = int(qty * percent)
        order = self.api.submit_order(
            symbol=self.symbol,
            qty=close_qty,  # abs(int(float(position.qty)))
            side=side,
            type="market",
            time_in_force="gtc",
            order_class="simple",
            client_order_id=order_id,
        )
        executed_at = order.submitted_at
        self.logger.info(f"Closed position with order ID {order.id} at {executed_at}")
        self.logger.info(f"Side: {side} Qty: {qty}")
        # update_log(executed_at, self.symbol, order.id, side, qty)
        return 1

    def cancel_position(self, order_id):
        self.api.cancel_order(order_id)

    def printURL(self):
        return print("Base URL: ", self.BASE_URL)

    # dir (1 is buy, 0 is sell)
    def submit_market_order(self, symb, qty, dir):
        move = "buy"
        if dir == 0:
            move = "sell"

        self.api.submit_order(
            symbol=symb,  # Replace with the ticker of the stock you want to buy
            qty=qty,
            side=move,
            type="market",
            time_in_force="gtc",
        )

    def submit_limit_order(self, symb, qty, dir):
        move = "buy"
        if dir == 0:
            move = "sell"

        self.api.submit_order(
            symbol=symb,  # Replace with the ticker of the stock you want to buy
            qty=qty,
            side=move,
            type="limit",
            time_in_force="gtc",
        )

    def submit_stop_price_order(self, symb, qty, dir, stop_price):
        move = "buy"
        if dir == 0:
            move = "sell"

        self.api.submit_order(
            symbol=symb,  # Replace with the ticker of the stock you want to buy
            qty=qty,
            side=move,
            type="trailing_stop",
            trail_price=stop_price,
            time_in_force="gtc",
        )

    def submit_stop_perc_order(self, symb, qty, dir, stop_perc):
        move = "buy"
        if dir == 0:
            move = "sell"

        self.api.submit_order(
            symbol=symb,  # Replace with the ticker of the stock you want to buy
            qty=qty,
            side=move,
            type="trailing_stop",
            trail_percent=stop_perc,
            time_in_force="gtc",
        )

    def listen(self):
        conn = tradeapi.stream2.StreamConn()
        # Handle updates on an order you've given a Client Order ID.
        # The r indicates that we're listening for a regex pattern.
        client_order_id = r"my_client_order_id"

        @conn.on(client_order_id)
        async def on_msg(conn, channel, data):
            # Print the update to the console.
            self.logger.info("Update for {}. Event: {}.".format(client_order_id, data["event"]))

        # Start listening for updates.
        conn.run(["trade_updates"])

    def check_position(self, symbol):
        # symb_status = self.SYMBOLS[symbol]
        position = self.api.get_position(symbol)
        portfolio = self.api.list_positions()
        for position in portfolio:
            self.logger.info("{} shares of {}".format(position.qty, position.symbol))
        return portfolio

    def open_short_position(self):
        pass

    def close_short_position(self):
        # Close the short position for the symbol
        positions = self.api.list_positions()
        for position in positions:
            if position.symbol == self.symbol and position.side == 'short':
                order = self.api.submit_order(
                    symbol=self.symbol,
                    qty=abs(int(float(position.qty))),
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                self.logger.info(f"Closed short position with order ID {order.id}")

        return 1
