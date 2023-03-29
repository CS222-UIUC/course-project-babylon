import pandas as pd
import mplfinance as mpf
from datetime import datetime
import pandas_datareader as web
import plotly.graph_objs as go
import plotly
import streamlit as st
from src.api import api_class
import streamlit_authenticator as stauth

file = "./src/web/AMZN.csv"
# file = "AMZN.csv"
data = pd.read_csv(file)
data.Date = pd.to_datetime(data.Date)
# data.info()
data = data.set_index("Date")

file2 = "./src/web/TSLA.csv"
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

username = None


if __name__ == "__main__":

    title_placeholder = (
        st.empty()
    )  # Creates an empty placeholder so that the text in it can be changed later
    title_placeholder.title("Select a stock on the left")
    current = ""
    with st.sidebar:
        username = st.text_input("Username", "username")
        # Initialize the session_state if it doesn't exist
        if "stocks" not in st.session_state:
            st.session_state["stocks"] = ["AMZN", "TSLA", "LMT"]

        # Add an input text field for the user to input a new stock symbol
        new_stock = st.text_input("Enter a new stock symbol:")

        # Add a button to add the new stock to the list
        if st.button("Add stock"):
            new_stock = new_stock.upper()
            if new_stock not in st.session_state["stocks"]:
                st.session_state["stocks"].append(new_stock)
            else:
                st.write("Stock already in the list")

        # Add an input text field for the user to input the stock symbol to delete
        stock_to_delete = st.text_input("Enter the stock symbol to delete:")

        # Add a button to delete the stock from the list
        if st.button("Delete stock"):
            stock_to_delete = stock_to_delete.upper()
            if stock_to_delete in st.session_state["stocks"]:
                st.session_state["stocks"].remove(stock_to_delete)
                st.write("Stock deleted")
            else:
                st.write("Stock not found")

        for stock in st.session_state["stocks"]:
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
