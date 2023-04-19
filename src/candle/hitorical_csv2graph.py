""" 
--Liang created Mar 10 2023--
last update Apr 19 2023

importable def that turn historical data to candle charts

"""

import pandas as pd
import mplfinance as mpf
from datetime import datetime
import pandas_datareader as web
import plotly.graph_objs as go
import plotly
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
import pandas_ta as ta
import requests
from api import api_class

Execution = api_class.Execution

# plot static trading signals, and/or addtional user-defined data.
#function for creating candle type 1
def type1_candle(file):
    data = pd.read_csv(file)
    data.columns
    data.Date = pd.to_datetime(data.Date)
    # data.info()
    data = data.set_index("Date")
    # mpf.plot(data)
    mpf.plot(
        data["2022-03":"2022-06"],
        figratio=(20, 12),
        type="candle",
        title="Amazon Price 2022",
        mav=(20),
        volume=True,
        tight_layout=True,
        style="yahoo",
    )
    return data


# plot historical data, time length changeable.
#function for creating candle type 2
def type2_candle(file):
    df = pd.read_csv(file)
    df = df.set_index(pd.DatetimeIndex(df["Date"].values))
    figure = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                low=df["Low"],
                high=df["High"],
                open=df["Open"],
                close=df["Close"],
            )
        ]
    )
    figure.update_layout(
        title="Amazon Price",
        yaxis_title="Amazon Stock Price USD ($)",
        xaxis_title="Date",
    )
    figure.show()
    return df


app = Dash()
# app = Dash(external_stylesheets= [dbc.themes.CYBORG])

#function for creating candle type 3
def type3_candle():
    app.layout = html.Div(
        [
            # html.H1("count-up",value = "0"),
            # html.H1("count-up"),
            html.Div(
                [
                    create_dropdown(["btcusd", "ethusd", "xrpusd"], "coin-select",),
                    create_dropdown(["60", "3600", "86400"], "timeframe-select",),
                    create_dropdown(["20", "50", "100"], "num-bars-select",),
                ],
                style={
                    "display": "flex",
                    "margin": "auto",
                    "width": "800px",
                    "justify-content": "space-around",
                },
            ),
            html.Div(
                [dcc.RangeSlider(0, 20, 1, value=[0, 20], id="range-slider"),],
                id="range-slider-container",
                style={"width": "800px", "margin": "auto", "padding-top": "30px"},
            ),
            dcc.Graph(id="candles"),
            dcc.Graph(id="indicator"),
            dcc.Interval(id="interval", interval=2000),
        ]
    )
    app.run_server(debug=True)


def create_dropdown(option, id_value):
    return html.Div(
        [
            html.H4(
                " ".join(id_value.replace("-", " ").split(" ")[:-1]),
                style={"padding": "0px 30px 0px 30px", "text-size": "15px"},
            ),
            dcc.Dropdown(option, id=id_value, value=option[0]),
        ],
        style={"padding": "0px 30px 0px 30px"},
    )


@app.callback(
    Output("range-slider-container", "children"), Input("num-bars-select", "value")
)
def update_rangeslider(num_bars):
    return dcc.RangeSlider(
        min=0,
        max=int(num_bars),
        step=int(int(num_bars) / 20),
        value=[0, int(num_bars)],
        id="range-slider",
    )


@app.callback(
    Output("candles", "figure"),
    Output("indicator", "figure"),
    Input("interval", "n_intervals"),
    Input("coin-select", "value"),
    Input("timeframe-select", "value"),
    Input("num-bars-select", "value"),
    Input("range-slider", "value"),
)
def update_figure(n_intervals, coin_pair, timeframe, num_bars, range_values):
    url = f"https://www.bitstamp.net/api/v2/ohlc/btcusd"
    params = {
        # "step":"60",
        "step": timeframe,
        "limit": int("30") + 14,
    }
    data = requests.get(url, params=params).json()["data"]["ohlc"]
    data = pd.DataFrame(data)
    data.timestamp = pd.to_datetime(data.timestamp, unit="s")

    data["rsi"] = ta.rsi(data.close.astype(float))
    data = data.iloc[14:]
    data = data.iloc[range_values[0] : range_values[1]]
    candles = go.Figure(
        data=[
            go.Candlestick(
                x=data.timestamp,
                open=data.open,
                high=data.high,
                low=data.low,
                close=data.close,
            )
        ]
    )
    # candles.update_layout(xaxis_rangeslider_visible = False,height = 400,template= "plotly_dark")
    # indicator = px.line(x=data.timestamp, y= data.rsi,height = 300, template= "plotly_dark")
    candles.update_layout(xaxis_rangeslider_visible=False, height=400)
    candles.update_layout(transition_duration=500)
    indicator = px.line(x=data.timestamp, y=data.rsi, height=300).update_layout(
        transition_duration=500
    )
    print(data)
    return candles, indicator


if __name__ == "__main__":
    type3_candle()
