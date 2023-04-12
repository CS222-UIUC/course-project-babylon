import mplfinance as mpf
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import pandas as pd
import threading
import time
from datetime import datetime

from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from datetime import timezone, datetime, timedelta


class Graph:
    """
        --Tass created Mar 26 2023--
        last update March 26 2023

        A class used to
        - plot real-time candle-stick graph

        """
    def __init__(self, symbol, client_api):
        self.symbol = symbol
        self.api = client_api
        self.df = self.get_historical_data()
        self.fig = go.FigureWidget()

    def get_historical_data(self):
        barset = self.api.get_crypto_bars(
            symbol=self.symbol,
            timeframe=TimeFrame(5, TimeFrameUnit.Minute),
            start=(datetime.now(timezone.utc) - timedelta(minutes=86400)).isoformat()
        ).df
        new_barset = barset[-50:]
        return new_barset

    def update_data(self):
        while True:
            try:
                last_trade = self.api.get_latest_trade(self.symbol)
                if last_trade.timestamp > self.df.index[-1]:
                    new_bar = {
                        'open': last_trade.price,
                        'high': last_trade.price,
                        'low': last_trade.price,
                        'close': last_trade.price,
                        'volume': last_trade.size
                    }
                    self.df.loc[last_trade.timestamp] = new_bar
                else:
                    self.df.at[self.df.index[-1], 'close'] = last_trade.price
                    self.df.at[self.df.index[-1], 'high'] = max(self.df.at[self.df.index[-1], 'high'], last_trade.price)
                    self.df.at[self.df.index[-1], 'low'] = min(self.df.at[self.df.index[-1], 'low'], last_trade.price)
                    self.df.at[self.df.index[-1], 'volume'] += last_trade.size

                time.sleep(60)
            except Exception as e:
                print(f"Error while updating data: {e}")
                time.sleep(60)


    def plot_candlestick(self):
        while True:
            try:
                self.fig = go.FigureWidget(
                    data=[
                        go.Candlestick(
                            x=self.df.index,
                            open=self.df['open'],
                            high=self.df['high'],
                            low=self.df['low'],
                            close=self.df['close']
                        )
                    ],
                    layout=go.Layout(
                        title=go.layout.Title(text=f'{self.symbol} Candlestick Graph'),
                        xaxis_rangeslider_visible=False,
                        xaxis_title='Time',
                        yaxis_title='Price',
                    )
                )
                self.fig.show()
                time.sleep(301)
            except Exception as e:
                print(f"Error while plotting: {e}")
                time.sleep(301)

    def start(self):
        data_thread = threading.Thread(target=self.update_data)
        plot_thread = threading.Thread(target=self.plot_candlestick)
        data_thread.start()
        plot_thread.start()

