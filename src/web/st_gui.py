import time
from datetime import datetime
from src.api.api_class import *
import pandas as pd
import mplfinance as mpf
import pandas_datareader as web
import plotly.graph_objs as go
import plotly
import streamlit as st
from src.api import api_class
import streamlit_authenticator as stauth

file = "src/web/AMZN.csv"
data = pd.read_csv(file)
data.Date = pd.to_datetime(data.Date)
# data.info()
data = data.set_index("Date")

file2 = "src/web/TSLA.csv"
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


def home_page():
    col_equity, col_buying_power, col_cash = st.columns(3)
    col_equity.metric("Equity", st.session_state.execution.api.get_account().equity)
    col_buying_power.metric("Buying Power", st.session_state.execution.api.get_account().buying_power)
    col_cash.metric("Cash", st.session_state.execution.api.get_account().cash)

def stock_page():
    pass

def main_page():
    # Initialize the execution class
    st.session_state.execution = Execution(st.session_state["login_credential"])
    # Create a dictionary to store the running state of each bot
    if "running_state" not in st.session_state:
        st.session_state.running_state = {"AMZN": False, "TSLA": False, "LMT": False}

    if "current_stock" not in st.session_state:
        st.session_state["current_stock"] = ""
        
    title_placeholder = (
        st.empty()
    )  # Creates an empty placeholder so that the text in it can be changed later
    # if st.session_state["current_stock"] == "":
    #     title_placeholder.title("Select a stock on the left")
        
    # else:
    #     title_placeholder.title(st.session_state["current_stock"])

    with st.sidebar:
        # Create a logout button
        
        if st.button("Logout"):
            st.session_state["is_logged_in"] = False
            st.experimental_rerun()

        
        # Initialize the session_state if it doesn't exist
        if "stocks" not in st.session_state:
            st.session_state["stocks"] = ["AMZN", "TSLA", "LMT"]

        # Add an input text field for the user to input a new stock symbol
        new_stock = st.text_input("Enter a new stock symbol:")

        # Add a button to add the new stock to the list
        if st.button("Add stock"):
            new_stock = new_stock.upper()
            if new_stock not in st.session_state["stocks"] and st.session_state.execution.add_symbol(new_stock) is True:
                st.session_state.running_state[new_stock] = False
                st.session_state["stocks"].append(new_stock)
                st.success("Stock added")
            else:
                st.error("Stock already exists or invalid symbol")

        # Add an input text field for the user to input the stock symbol to delete
        stock_to_delete = st.text_input("Enter the stock symbol to delete:")

        # Add a button to delete the stock from the list
        if st.button("Delete stock"):
            stock_to_delete = stock_to_delete.upper()
            if stock_to_delete in st.session_state["stocks"] and st.session_state.execution.delete_symbol(stock_to_delete) is True:
                st.session_state.running_state.pop(stock_to_delete)
                st.session_state["stocks"].remove(stock_to_delete)
                st.success("Stock deleted")
            else:
                st.error("Stock not found or delete failed")
        if st.button("Home", use_container_width=True):
            current = ""
            st.session_state["current_stock"] = ""
        for stock in st.session_state["stocks"]:
            if st.button(stock, use_container_width=True):
                st.session_state["current_stock"] = stock
                current = st.session_state["current_stock"]
                
    
    if st.session_state["current_stock"] != "":
        # current = st.session_state["current_stock"]
        title_placeholder.title(st.session_state["current_stock"])
        options = ["Trading History", "Graph", "Bot Info", "Settings"]
        selected_option = st.selectbox("Select an option", options)

        if selected_option == "Trading History":
            if current == "AMZN":
                st.dataframe(data)
            if current == "TSLA":
                st.dataframe(data2)
            else:
                st.text("This should be data")
        elif selected_option == "Graph":
            if current == "AMZN":
                st.plotly_chart(figure)
            else:
                st.text("This should be graph")
        elif selected_option == "Bot Info":
            current = st.session_state["current_stock"]
            print(current)
            is_running = st.session_state.running_state[current]
            if not is_running:
                if st.button("Create bot"):
                    st.session_state.execution.create_bot(current)
                    st.session_state.running_state[current] = True
                    st.experimental_rerun()
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Reset bot"):
                        st.session_state.execution.reset_bot(current)
                        st.session_state.running_state[current] = False
                        st.experimental_rerun()
                with col2:
                    if st.button("Pause bot"):
                        st.session_state.execution.pause_bot(current)
                with col3:
                    if st.button("Start bot"):
                        st.session_state.execution.start_bot(current)
        elif selected_option == "Settings":
            st.text("This is setting")

    else:
        title_placeholder.title("Select a stock on the left")
        home_page()
    #     st.error("No stock selected")


def login_page():
    with st.form("login_form"):
        api_key = st.text_input("Enter your API key:")
        secret = st.text_input("Enter your secret:", type="password")
        st.session_state["api_key"] = api_key
        st.session_state["secret"] = secret
        submit_button = st.form_submit_button("Login")

    if submit_button:
        login_credential = LOGIN(api_key, secret)
        if login_credential != -1:
            st.session_state["is_logged_in"] = True
            st.session_state["login_credential"] = login_credential
            st.experimental_rerun()
        else:
            st.error("Invalid API key or secret. Please try again.")


if __name__ == "__main__":
    # Initialize api_key and secret in the session_state if they don't exist
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = None
    if "secret" not in st.session_state:
        st.session_state["secret"] = None

    # Initialize the execution if it doesn't exist
    if "execution" not in st.session_state:
        st.session_state["execution"] = None
    # Initialize the login_credential if it doesn't exist
    if "login_credential" not in st.session_state:
        st.session_state["login_credential"] = None

    # Initialize the session_state if it doesn't exist
    if "is_logged_in" not in st.session_state:
        st.session_state["is_logged_in"] = False

    if st.session_state["is_logged_in"]:
        main_page()
        
    else:
        login_page()
