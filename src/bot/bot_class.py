import alpaca_trade_api as tradeapi
import time
import datetime
import pandas as pd

# file = pd.read_csv("src/api/logs_database.csv")
logs = []


class BOT:
    """ 
    --Tass created Feb 16 2023--
    last update March 3 2023
    
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
        self.paused = True

    def start(self):
        while not self.paused:
            try:
                self.run_strategy()
            except Exception as e:
                print(f"Error in strategy: {e}")
                time.sleep(60)

    def pause(self):
        self.paused = True

    def run_strategy(self):
        # Get historical price data
        bars = self.api.get_barset(self.symbol, self.timeframe, limit=self.rsi_period)
        prices = bars[self.symbol].df["close"].values

        # Calculate RSI
        rsi = talib.RSI(prices, timeperiod=self.rsi_period)[-1]

        # Check if RSI is above upper threshold and open a short position
        if rsi > self.rsi_upper:
            if not self.has_short_position():
                self.open_short_position()

        # Check if RSI is below lower threshold and close the short position
        elif rsi < self.rsi_lower:
            if self.has_short_position():
                self.close_short_position()

    def has_short_position(self):
        # Check if there is an open short position for the symbol
        positions = self.api.list_positions()
        for position in positions:
            if position.symbol == self.symbol and position.side == "sell":
                return True
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
        print(f"Opened position with order ID {order.id} at {executed_at}")
        update_log(executed_at, self.symbol, order.id, side, qty)
        return [executed_at, order, "open", side, qty]

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
        print(f"Closed position with order ID {order.id} at {executed_at}")
        update_log(executed_at, self.symbol, order.id, side, qty)
        return [executed_at, order, "close", close_qty]

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

    def read_1min_data(self, symbol):
        market_data = self.api.get_barset(symbol, "minute", limit=1)
        return market_data

    def listen(self):
        conn = tradeapi.stream2.StreamConn()
        # Handle updates on an order you've given a Client Order ID.
        # The r indicates that we're listening for a regex pattern.
        client_order_id = r"my_client_order_id"

        @conn.on(client_order_id)
        async def on_msg(conn, channel, data):
            # Print the update to the console.
            print("Update for {}. Event: {}.".format(client_order_id, data["event"]))

        # Start listening for updates.
        conn.run(["trade_updates"])

    def check_position(self, symbol):
        # symb_status = self.SYMBOLS[symbol]
        position = self.api.get_position(symbol)
        portfolio = self.api.list_positions()
        for position in portfolio:
            print("{} shares of {}".format(position.qty, position.symbol))
        return portfolio


def update_log(timestamp, symbol, order_id, direction, qty):
    logs.append((timestamp, symbol, order_id, direction, qty))
    print("logs updated")
