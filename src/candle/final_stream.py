from statistics import mode
from alpaca_trade_api.stream import Stream
from datetime import datetime,timedelta
from anyio import current_time
import pandas as pd
import logging
import dummy
import os
import time
from matplotlib.pyplot import plot
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import dummy
import threading
API_KEY = "PKNKABC4NQ6UURX5RU4R"
SECRET_KEY = "0GOzkmT1F5W9rs8czJ90YAXKZrBn6jee3BgGo9le"

dummy_path = dummy.__file__
async def trade_bars(bars):
    temp_df = pd.DataFrame(
        columns=["time", "open", "high", "low", "close", "volume", "tic", "vwap"]
    )
    present_time = datetime.utcfromtimestamp(bars.timestamp/10**9).strftime("%Y-%m-%d %H:%M:%S")
    temp_df["time"] = [present_time]
    temp_df["open"] = [bars.open]
    temp_df["high"] = [bars.high]
    temp_df["low"] = [bars.low]
    temp_df["close"] = [bars.close]
    temp_df["volume"] = [bars.volume]
    temp_df["tic"] = [bars.symbol]
    if bars.symbol in ['ETHUSD','BTCUSD']:
        temp_df["exchange"] = [bars.exchange]
    else:
        pass
    temp_df["vwap"] = [bars.vwap]

    temp_df.to_csv("bars.csv", mode="a", header=False)

    print(bars)
    with open(dummy_path,"w") as fp:
        fp.write(f"timestamp = '{datetime.now()}'")

def csv_handling(file_name: str, columns_list: list):
    if os.path.exists(file_name):
        try:
            trade_temp_df = pd.read_csv(file_name)
        except:
            print("The file doesn't exist, creating it")
            trade_temp_df = pd.DataFrame(columns=columns_list)
            trade_temp_df.to_csv(file_name)
        if trade_temp_df.empty:
            trade_temp_df = pd.DataFrame(columns=columns_list)
            trade_temp_df.to_csv(file_name)
        else:
            pass
    else:
        trade_temp_df = pd.DataFrame(columns=columns_list)
        trade_temp_df.to_csv(file_name)

def run_connection(stream):
    try:
        stream.run()
    except KeyboardInterrupt:
        print("Interrupted execution by the user")
        loop.run_until_complete(stream.stop_ws())
        exit(0)
    except Exception as e:
        print(f'Exception from websocket connection: {e}')
    finally:
        print('Trying to re-establish connection')
        time.sleep(3)
        run_connection(stream)

def plot_data():
    df = pd.read_csv("bars.csv")
    tic_groups = df.groupby(by=['tic'],sort=False)
    
    tics = []
    figs = []
    for tic in tic_groups:
        df = tic[1]
        fig = go.Figure(data=[go.Candlestick(x=df['time'],
                            open=df['open'],high=df['high'],low=df['low'],close=df.close)])
        fig.update_layout(xaxis_rangeslider_visible=False)
        tics.append(tic[0])
        figs.append(fig)
    return tics,figs

def plotting():
    tics,figs = plot_data()
    for plots in zip(tics,figs):
        st.write(f'CandleSticks graph for {plots[0]}')
        st.plotly_chart(plots[1])
    return

# def start(self):
#         data_thread = threading.Thread(target=self.run_connection)
#         plot_thread = threading.Thread(target=self.plotting)
#         data_thread.start()
#         plot_thread.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stream = Stream(
        API_KEY, SECRET_KEY, base_url="https://paper-api.alpaca.markets", raw_data=False,
        data_feed='iex',
        crypto_exchanges = ['CBSE']
    )
    csv_handling(
        "bars.csv",
        columns_list=["time", "open", "high", "low", "close", "volume", "tic", "exchange","vwap"],
    )
    # stream.subscribe_bars(trade_bars,'LMT')
    stream.subscribe_crypto_bars(trade_bars, "ETHUSD")
    stream.subscribe_crypto_bars(trade_bars, "BTCUSD")
    run_connection(stream)
    # start()

    print("Complete")
