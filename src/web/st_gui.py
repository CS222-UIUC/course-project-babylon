import pandas as pd
import mplfinance as mpf
from datetime import datetime
import pandas_datareader as web
import plotly.graph_objs as go
import plotly
import streamlit as st

file = "./AMZN.csv"
# file = "AMZN.csv"
data = pd.read_csv(file)
data.Date = pd.to_datetime(data.Date)
# data.info()
data = data.set_index("Date")

file2 = "./TSLA.csv"
# = "TSLA.csv"
data2 = pd.read_csv(file2)
data2.Date = pd.to_datetime(data2.Date)
# data.info()
data2 = data2.set_index("Date")

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
    title="Amazon Price", yaxis_title="Amazon Stock Price USD ($)", xaxis_title="Date"
)
# figure.show()

if __name__ == "__main__":

    title_placeholder = (
        st.empty()
    )  # Creates an empty placeholder so that the text in it can be changed later
    title_placeholder.title("Select a stock on the left")
    current = ""
    with st.sidebar:
        st.text("User: Unknown")

        stocks = ["AMZN", "TSLA", "LMT"]
        for stock in stocks:
            if st.button(stock, use_container_width=True):
                current = stock
                title_placeholder.title(stock)

    if current != "":
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Trading History", "Graph", "Bot Info", "Settings"]
        )
        # data = [data, data2]
        with tab1:
            if current == "AMZN":
                st.dataframe(data)
            if current == "TSLA":
                st.dataframe(data2)
            else:
                st.text("This should be data")
        with tab2:
            if current == "AMZN":
                st.plotly_chart(figure)
            else:
                st.text("This should be graph")
        with tab3:
            st.text("This is information of bot")
        with tab4:
            st.text("This is setting")
    else:
        name = st.text("Main Page")
