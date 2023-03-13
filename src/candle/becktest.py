# Alpaca for data
import alpaca_trade_api as api
from alpaca_trade_api.rest import TimeFrame

# pandas for analysis
import pandas as pd

# Plotly for charting
import plotly.graph_objects as go
import plotly.express as px

# Set default charting for pandas to plotly
pd.options.plotting.backend = "plotly"

# symbols we will be looking at
btc = "BTCUSD"
spy = "SPY"

# start dates and end dates for backtest
start_date = "2021-01-01"
end_date = "2021-10-20"

# time frame for backtests
timeframe = TimeFrame.Day

# periods for our SMA's
SMA_fast_period = 5
SMA_slow_period = 13

# Our API keys for Alpaca
API_KEY = "YOUR_ALPACA_API_KEY"
API_SECRET = "YOUR_ALPACA_API_SECRET"

# Setup instance of alpaca api
alpaca = api.REST(API_KEY, API_SECRET)

# # # Request historical bar data for SPY and BTC using Alpaca Data API
# for equities, use .get_bars
spy_data = alpaca.get_bars(spy, timeframe, start_date, end_date).df

# for crypto, use .get_crypto_bars, from multiple exchanges
btc_data = alpaca.get_crypto_bars(btc, timeframe, start_date, end_date).df

# display crypto bar data
btc_data