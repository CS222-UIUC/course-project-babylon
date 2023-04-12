import unittest
from graph_class import *
import pandas as pd
from src.api.unit_tests_api import CLIENT_API


class Graph_test_cases(unittest.TestCase):
    def test_get_hist_data(self):
        symbol = 'BTCUSD'

        barset = CLIENT_API.get_crypto_bars(
            symbol=symbol,
            timeframe=TimeFrame(59, TimeFrameUnit.Minute),
            start=(datetime.now(timezone.utc) - timedelta(minutes=86400)).isoformat()
        ).df

        df = barset[-100:]

        print(df)
        colors = ['#00b300' if df.iloc[-1]['open'] > df.iloc[-2]['close'] else '#e60000'] * len(df.index)
        figure = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    low=df["low"],
                    high=df["high"],
                    open=df["open"],
                    close=df["close"],
                )
            ]
        )
        figure.show()

        fig = go.FigureWidget(
            data=[
                go.Candlestick(
                    x=new_barset.index,
                    open=new_barset['open'],
                    high=new_barset['high'],
                    low=new_barset['low'],
                    close=new_barset['close'],
                    increasing = dict(line=dict(color=colors[1])),
                    decreasing = dict(line=dict(color=colors[0]))
                )
            ],
            layout=go.Layout(
                title=go.layout.Title(text=f'{symbol} Candlestick Graph'),
                xaxis_rangeslider_visible=False,
                xaxis_title='Time',
                yaxis_title='Price',
            )
        )
        fig.show()



    def test_graph(self):
        symbol = 'BTCUSD'

        g = Graph(symbol, CLIENT_API)
        g.start()




if __name__ == '__main__':
    unittest.main()
