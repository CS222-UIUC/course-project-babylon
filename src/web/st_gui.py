from src.api.api_class import *
from src.candle.grass import *
import pandas as pd
import streamlit as st


def main_page():
    # Initialize the execution if it doesn't exist
    if "execution" not in st.session_state:
        st.session_state.execution = Execution(st.session_state["login_credential"])
        # create an empty folder named as login_credential if it doesn't exist
        if not os.path.exists("./data/" + st.session_state.api_key):
            os.makedirs("./data/" + st.session_state.api_key)

    # Initialize the session_state if it doesn't exist
    if "stocks" not in st.session_state:
        # create a csv file named stocks.csv if it doesn't exist
        if not os.path.exists("./data/" + st.session_state.api_key + "/stocks.csv"):
            # create an empty csv file
            pd.DataFrame(columns=["Names"]).to_csv(
                "./data/" + st.session_state.api_key + "/stocks.csv", index=False
            )
        # read the csv file and store the symbols in the session_state
        st.session_state["stocks"] = pd.read_csv(
            "./data/" + st.session_state.api_key + "/stocks.csv"
        ).Names.tolist()

        # add the symbols to the execution and create csv file named symbol.csv
        for symbol in st.session_state["stocks"]:
            st.session_state.execution.add_symbol(symbol)
            if not os.path.exists("./data/" + st.session_state.api_key + "/" + symbol + ".csv"):
                # create an empty csv file
                pd.DataFrame(columns=["Action", "Date", "Time", "Transaction"]).to_csv(
                    "./data/" + st.session_state.api_key + "/" + symbol + ".csv", index=False
                )

    # Create a dictionary to store the running state of each bot
    if "running_state" not in st.session_state:
        st.session_state["running_state"] = {}
        for symbol in st.session_state["stocks"]:
            st.session_state["running_state"][symbol] = False

    if "current_stock" not in st.session_state:
        st.session_state["current_stock"] = ""

    title_placeholder = (
        st.empty()
    )  # Creates an empty placeholder so that the text in it can be changed later

    with st.sidebar:
        col1, col2 = st.columns(2)
        with col1:
            # User profile picture and username
            st.image("https://www.pngkit.com/png/full/165-1650218_at-the-movies-will-smith-meme-tada.png", width=145)
        with col2:
            if st.button("Dashboard", use_container_width=True):
                st.session_state["current_stock"] = ""
            if st.button("Logout", use_container_width=True):
                st.session_state["is_logged_in"] = False
                st.experimental_rerun()
        # Only display the first five characters of the user api key
        st.text(f"API_KEY: {st.session_state.api_key[:5]}{'*' * 10}")

        if "add_status" not in st.session_state:
            st.session_state["add_status"] = 0  # 0 = not added, 1 = added, 2 = failed

        if "delete_status" not in st.session_state:
            st.session_state["delete_status"] = 0  # 0 = not deleted, 1 = deleted, 2 = failed

        if "update_status" not in st.session_state:
            st.session_state["update_status"] = 0  # 0 = not updated, 1 = updated, 2 = failed

        # Create an empty placeholder to display the success/failure message
        message_placeholder = st.empty()
        if st.session_state["add_status"] != 0:
            if st.session_state["add_status"] == 1:
                message_placeholder.success("Stock successfully added")
            else:
                message_placeholder.error("Stock already exists or invalid symbol")
            st.session_state["add_status"] = 0
        elif st.session_state["delete_status"] != 0:
            if st.session_state["delete_status"] == 1:
                message_placeholder.success("Stock successfully deleted")
            else:
                message_placeholder.error("Stock not found or delete failed")
            st.session_state["delete_status"] = 0
        elif st.session_state["update_status"] != 0:
            if st.session_state["update_status"] == 1:
                message_placeholder.success("Bot setting successfully updated")
            else:
                message_placeholder.error("Bot setting update failed")
            st.session_state["update_status"] = 0

        # Add an input text field for the user to input a new stock symbol
        new_stock = st.text_input("Enter a new stock symbol:")

        # Add a button to add the new stock to the list
        if st.button("Add stock"):
            new_stock = new_stock.upper()
            if new_stock not in st.session_state["stocks"] \
                    and new_stock != "HOME" and st.session_state.execution.add_symbol(new_stock) is True:
                st.session_state.running_state[new_stock] = False
                st.session_state["stocks"].append(new_stock)
                st.session_state["add_status"] = 1
                # Update the csv file
                pd.DataFrame(st.session_state["stocks"], columns=["Names"]).to_csv(
                    "./data/" + st.session_state.api_key + "/stocks.csv", index=False
                )
                # Create a csv file for the new stock
                pd.DataFrame(columns=["Action", "Date", "Time", "Transaction"]).to_csv(
                    "./data/" + st.session_state.api_key + "/" + new_stock + ".csv", index=False
                )
                st.experimental_rerun()
            else:
                st.error("Stock already exists or invalid symbol")
                st.session_state["add_status"] = 2
                st.experimental_rerun()

        # Add an input text field for the user to input the stock symbol to delete
        stock_to_delete = st.text_input("Enter the stock symbol to delete:")

        # Add a button to delete the stock from the list
        if st.button("Delete stock"):
            stock_to_delete = stock_to_delete.upper()
            if stock_to_delete in st.session_state["stocks"] and st.session_state.execution.delete_symbol(
                    stock_to_delete) is True:
                st.session_state["current_stock"] = ""
                st.session_state.running_state.pop(stock_to_delete)
                st.session_state["stocks"].remove(stock_to_delete)
                st.session_state["delete_status"] = 1
                # Update the csv file
                pd.DataFrame(st.session_state["stocks"], columns=["Names"]).to_csv(
                    "./data/" + st.session_state.api_key + "/stocks.csv", index=False
                )
                # Delete the csv file for the stock
                os.remove("./data/" + st.session_state.api_key + "/" + stock_to_delete + ".csv")
                st.experimental_rerun()
            else:
                st.error("Stock not found or delete failed")
                st.session_state["delete_status"] = 2
                st.experimental_rerun()

        for stock in st.session_state["stocks"]:
            if st.button(stock, use_container_width=True, key=f"stock_button_{stock}"):
                st.session_state["current_stock"] = stock

    if st.session_state["current_stock"] != "":
        st.empty()

        current = st.session_state["current_stock"]
        title_placeholder.title(current)
        options = ["Graph", "Bot Status", "Bot Settings"]
        selected_option = st.selectbox("Select an option", options)

        if selected_option == "Graph":
            display_graph(current)
        elif selected_option == "Bot Status":
            st.empty()
            st.empty()
            is_running = st.session_state.running_state[current]
            if not is_running:
                if st.button("Create bot"):
                    st.session_state.execution.create_bot(current)
                    st.session_state.running_state[current] = True
                    st.experimental_rerun()
            else:
                # Get the current bot paused state
                paused = st.session_state.execution.get_paused(current)
                if paused:
                    st.error("Bot is paused")
                else:
                    st.success("Bot is running")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Reset bot", use_container_width=True):
                        st.session_state.execution.reset_bot(current)
                        st.session_state.running_state[current] = False
                        st.experimental_rerun()
                with col2:
                    if st.button("Pause bot", use_container_width=True):
                        st.session_state.execution.pause_bot(current)
                        st.experimental_rerun()
                with col3:
                    if st.button("Start bot", use_container_width=True):
                        st.session_state.execution.start_bot(current)
                        st.experimental_rerun()

                st.session_state.execution.simulate_trading(current, st.session_state.api_key)
        elif selected_option == "Bot Settings":
            is_running = st.session_state.running_state[current]
            if not is_running:
                st.error("Bot must be running to change settings, please create a bot first under the Bot Info tab")
            else:
                # Get the current bot time_frame, rsi_period, rsi_upper and rsi_lower
                time_frame_old = st.session_state.execution.get_timeframe(current)
                rsi_period_old = st.session_state.execution.get_rsi_period(current)
                rsi_upper_old = st.session_state.execution.get_rsi_upper(current)
                rsi_lower_old = st.session_state.execution.get_rsi_lower(current)

                # Display the current settings in the text input fields
                time_frame = st.text_input("Time frame", time_frame_old, help="Choose from 1Min, 5Min, 15Min, 1H, 1D")
                rsi_period = st.text_input("RSI period", rsi_period_old)
                rsi_upper = st.text_input("RSI upper", rsi_upper_old)
                rsi_lower = st.text_input("RSI lower", rsi_lower_old)

                # Add a button to update the settings
                if st.button("Save"):
                    # Check if the new settings are valid
                    if time_frame in ["1Min", "5Min", "15Min", "1H",
                                      "1D"] and rsi_period.isdigit() and rsi_upper.isdigit() \
                            and rsi_lower.isdigit():
                        # Update the settings
                        st.session_state.execution.set_timeframe(current, time_frame)
                        st.session_state.execution.set_rsi_period(current, int(rsi_period))
                        st.session_state.execution.set_rsi_upper(current, int(rsi_upper))
                        st.session_state.execution.set_rsi_lower(current, int(rsi_lower))
                        st.session_state["update_status"] = 1
                        st.experimental_rerun()
                    else:
                        st.error("Invalid settings")
                        st.session_state["update_status"] = 2
                        st.experimental_rerun()

    else:
        title_placeholder.title("Dashboard")
        col_equity, col_buying_power, col_cash = st.columns(3)
        col_equity.metric("Equity", st.session_state.execution.api.get_account().equity)
        col_buying_power.metric("Buying Power", st.session_state.execution.api.get_account().buying_power)
        col_cash.metric("Cash", st.session_state.execution.api.get_account().cash)


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
