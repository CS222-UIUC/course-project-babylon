# Alpaca for data
import alpaca_trade_api as api
from alpaca_trade_api.rest import TimeFrame

# pandas for analysis
import pandas as pd

API_SECRET = "0GOzkmT1F5W9rs8czJ90YAXKZrBn6jee3BgGo9le"
API_KEY = "PKNKABC4NQ6UURX5RU4R"
BASE_URL = 'https://paper-api.alpaca.markets'

# Plotly for charting
import plotly.graph_objects as go
import plotly.express as px

# Set default charting for pandas to plotly
pd.options.plotting.backend = "plotly"


# Setup instance of alpaca api
def backtest_set_up(
    API_KEY, API_SECRET, crypto_name="ETH", stock_name="BILI",
):
    alpaca = api.REST(API_KEY, API_SECRET)
    crypto_name = crypto_name
    stock_name = stock_name
    return alpaca, crypto_name, stock_name


def get_stock_df(
    alpaca,
    stock_name="BILI",
    timeframe=TimeFrame.Day,
    start_date="2021-01-01",
    end_date="2021-10-20",
):
    stock_data = alpaca.get_bars(stock_name, timeframe, start_date, end_date).df
    return stock_data


def get_crtpyo_df(
    alpaca,
    crypto_name="ETH",
    timeframe=TimeFrame.Day,
    start_date="2021-01-01",
    end_date="2021-10-20",
):
    crypto_name = crypto_name + "USD"
    crypto_data = alpaca.get_crypto_bars(
        crypto_name, timeframe, start_date, end_date
    ).df
    return crypto_data


# Comparing stock & crypto currency
# default computing the 5-day SMA and 13-day SMA, and 252 trading days in the current year
def CS_charts_n_sharp(
    stock_df,
    crypto_df,
    stock_name,
    crypto_name,
    SMA_fast_period=5,
    SMA_slow_period=13,
    trading_days=252,
):
    # Keep data from only CBSE exchange
    crypto_df = crypto_df[crypto_df["exchange"] == "CBSE"]

    # keep only the daily close data column
    crypto_df = crypto_df.filter(["close"])

    crypto_df.rename(columns={"close": crypto_name}, inplace=True)

    # keep only the date part of our timestamp index
    crypto_df.index = crypto_df.index.map(lambda timestamp: timestamp.date)

    stock_df = stock_df.filter(["close"])
    stock_df.rename(columns={"close": stock_name}, inplace=True)
    stock_df.index = stock_df.index.map(lambda timestamp: timestamp.date)
    data = crypto_df.join(stock_df, how="outer")
    data.index.name = "date"
    data = data.ffill()
    data[stock_name + "_daily_return"] = data[stock_name].pct_change()
    data[crypto_name + "_daily_return"] = data[crypto_name].pct_change()

    data[stock_name + "_return"] = (
        data[stock_name + "_daily_return"].add(1).cumprod().sub(1)
    )
    data[crypto_name + "_return"] = (
        data[crypto_name + "_daily_return"].add(1).cumprod().sub(1)
    )

    cumulative_return_fig = px.line(
        data, x=data.index, y=[stock_name + "_return", crypto_name + "_return"]
    )
    data["slow_SMA"] = data[crypto_name].rolling(SMA_slow_period).mean()
    data["fast_SMA"] = data[crypto_name].rolling(SMA_fast_period).mean()

    data.dropna(inplace=True)

    SMA_fig = data.plot(y=[crypto_name, "slow_SMA", "fast_SMA"])
    # calculating when 5-day SMA crosses over 13-day SMA
    crossover = data[
        (data["fast_SMA"] > data["slow_SMA"])
        & (data["fast_SMA"].shift() < data["slow_SMA"].shift())
    ]

    # calculating when 5-day SMA crosses unsw 13-day SMA
    crossunder = data[
        (data["fast_SMA"] < data["slow_SMA"])
        & (data["fast_SMA"].shift() > data["slow_SMA"].shift())
    ]
    # Plot green upward facing triangles at crossovers
    fig1 = px.scatter(
        crossover,
        x=crossover.index,
        y="slow_SMA",
        color_discrete_sequence=["green"],
        symbol_sequence=[49],
    )

    # Plot red downward facing triangles at crossunders
    fig2 = px.scatter(
        crossunder,
        x=crossunder.index,
        y="fast_SMA",
        color_discrete_sequence=["red"],
        symbol_sequence=[50],
    )

    # Plot slow sma, fast sma and price
    fig3 = data.plot(y=[crypto_name, "fast_SMA", "slow_SMA"])

    SMA_Crossovers_fig = go.Figure(data=fig1.data + fig2.data + fig3.data)
    SMA_Crossovers_fig.update_traces(marker={"size": 13})
    # New column for orders
    crossover["order"] = "buy"
    crossunder["order"] = "sell"

    # Combine buys and sells into 1 data frame
    orders = pd.concat(
        [crossover[[crypto_name, "order"]], crossunder[[crypto_name, "order"]]]
    ).sort_index()

    # new dataframe with market data and orders merged
    portfolio = pd.merge(data, orders, how="outer", left_index=True, right_index=True)
    # "backtest" of our buy and hold strategies
    portfolio[stock_name + "_buy_&_hold"] = (
        portfolio[stock_name + "_return"] + 1
    ) * 10000
    portfolio[crypto_name + "_buy_&_hold"] = (
        portfolio[crypto_name + "_return"] + 1
    ) * 10000
    # forward fill any missing data points in our buy & hold strategies
    # and forward fill Crypto_daily_return for missing data points
    portfolio[
        [
            crypto_name + "_buy_&_hold",
            stock_name + "_buy_&_hold",
            crypto_name + "_daily_return",
        ]
    ] = portfolio[
        [
            crypto_name + "_buy_&_hold",
            stock_name + "_buy_&_hold",
            crypto_name + "_daily_return",
        ]
    ].ffill()
    ### Backtest of SMA crossover strategy
    active_position = False
    equity = 10000

    # Iterate row by row of our historical data
    for index, row in portfolio.iterrows():

        # change state of position
        if row["order"] == "buy":
            active_position = True
        elif row["order"] == "sell":
            active_position = False

        # update strategy equity
        if active_position:
            portfolio.loc[index, crypto_name + "_SMA_crossover"] = (
                row[crypto_name + "_daily_return"] + 1
            ) * equity
            equity = portfolio.loc[index, crypto_name + "_SMA_crossover"]
        else:
            portfolio.loc[index, crypto_name + "_SMA_crossover"] = equity
    strategy_performance_fig = px.line(
        portfolio[
            [
                crypto_name + "_SMA_crossover",
                crypto_name + "_buy_&_hold",
                stock_name + "_buy_&_hold",
            ]
        ],
        color_discrete_sequence=["green", "blue", "red"],
    )
    portfolio[crypto_name + "_SMA_daily_returns"] = portfolio[
        crypto_name + "_SMA_crossover"
    ].pct_change()

    mean_daily_return = portfolio[crypto_name + "_SMA_daily_returns"].mean()
    std_daily_return = portfolio[crypto_name + "_SMA_daily_returns"].std()
    stock_mean_daily_return = portfolio[stock_name + "_daily_return"].mean()
    daily_sharpe_ratio = (
        mean_daily_return - stock_mean_daily_return
    ) / std_daily_return

    annualized_sharpe_ratio = daily_sharpe_ratio * (trading_days ** 0.5)
    # return annualized_sharpe_ratio
    return (
        annualized_sharpe_ratio,
        cumulative_return_fig,
        SMA_fig,
        SMA_Crossovers_fig,
        strategy_performance_fig,
    )


# Comparing stock & stock
def SS_charts_n_sharp(
    stock1_df,
    stock2_df,
    stock1_name,
    stock2_name,
    SMA_fast_period=5,
    SMA_slow_period=13,
    trading_days=252,
):

    stock2_df = stock2_df.filter(["close"])
    stock2_df.rename(columns={"close": stock2_name}, inplace=True)
    stock2_df.index = stock2_df.index.map(lambda timestamp: timestamp.date)

    stock1_df = stock1_df.filter(["close"])
    stock1_df.rename(columns={"close": stock1_name}, inplace=True)
    stock1_df.index = stock1_df.index.map(lambda timestamp: timestamp.date)

    data = stock2_df.join(stock1_df, how="outer")
    data.index.name = "date"
    data = data.ffill()
    data[stock1_name + "_daily_return"] = data[stock1_name].pct_change()
    data[stock2_name + "_daily_return"] = data[stock2_name].pct_change()

    data[stock1_name + "_return"] = (
        data[stock1_name + "_daily_return"].add(1).cumprod().sub(1)
    )
    data[stock2_name + "_return"] = (
        data[stock2_name + "_daily_return"].add(1).cumprod().sub(1)
    )

    cumulative_return_fig = px.line(
        data, x=data.index, y=[stock1_name + "_return", stock2_name + "_return"]
    )
    data["slow_SMA"] = data[stock2_name].rolling(SMA_slow_period).mean()
    data["fast_SMA"] = data[stock2_name].rolling(SMA_fast_period).mean()

    data.dropna(inplace=True)

    SMA_fig = data.plot(y=[stock2_name, "slow_SMA", "fast_SMA"])
    # calculating when 5-day SMA crosses over 13-day SMA
    crossover = data[
        (data["fast_SMA"] > data["slow_SMA"])
        & (data["fast_SMA"].shift() < data["slow_SMA"].shift())
    ]

    # calculating when 5-day SMA crosses unsw 13-day SMA
    crossunder = data[
        (data["fast_SMA"] < data["slow_SMA"])
        & (data["fast_SMA"].shift() > data["slow_SMA"].shift())
    ]
    # Plot green upward facing triangles at crossovers
    fig1 = px.scatter(
        crossover,
        x=crossover.index,
        y="slow_SMA",
        color_discrete_sequence=["green"],
        symbol_sequence=[49],
    )

    # Plot red downward facing triangles at crossunders
    fig2 = px.scatter(
        crossunder,
        x=crossunder.index,
        y="fast_SMA",
        color_discrete_sequence=["red"],
        symbol_sequence=[50],
    )

    # Plot slow sma, fast sma and price
    fig3 = data.plot(y=[stock2_name, "fast_SMA", "slow_SMA"])

    SMA_Crossovers_fig = go.Figure(data=fig1.data + fig2.data + fig3.data)
    SMA_Crossovers_fig.update_traces(marker={"size": 13})
    # New column for orders
    crossover["order"] = "buy"
    crossunder["order"] = "sell"

    # Combine buys and sells into 1 data frame
    orders = pd.concat(
        [crossover[[stock2_name, "order"]], crossunder[[stock2_name, "order"]]]
    ).sort_index()

    # new dataframe with market data and orders merged
    portfolio = pd.merge(data, orders, how="outer", left_index=True, right_index=True)
    # "backtest" of our buy and hold strategies
    portfolio[stock1_name + "_buy_&_hold"] = (
        portfolio[stock1_name + "_return"] + 1
    ) * 10000
    portfolio[stock2_name + "_buy_&_hold"] = (
        portfolio[stock2_name + "_return"] + 1
    ) * 10000
    # forward fill any missing data points in our buy & hold strategies
    # and forward fill crypto_daily_return for missing data points
    portfolio[
        [
            stock2_name + "_buy_&_hold",
            stock1_name + "_buy_&_hold",
            stock2_name + "_daily_return",
        ]
    ] = portfolio[
        [
            stock2_name + "_buy_&_hold",
            stock1_name + "_buy_&_hold",
            stock2_name + "_daily_return",
        ]
    ].ffill()
    ### Backtest of SMA crossover strategy
    active_position = False
    equity = 10000

    # Iterate row by row of our historical data
    for index, row in portfolio.iterrows():

        # change state of position
        if row["order"] == "buy":
            active_position = True
        elif row["order"] == "sell":
            active_position = False

        # update strategy equity
        if active_position:
            portfolio.loc[index, stock2_name + "_SMA_crossover"] = (
                row[stock2_name + "_daily_return"] + 1
            ) * equity
            equity = portfolio.loc[index, stock2_name + "_SMA_crossover"]
        else:
            portfolio.loc[index, stock2_name + "_SMA_crossover"] = equity
    strategy_performance_fig = px.line(
        portfolio[
            [
                stock2_name + "_SMA_crossover",
                stock2_name + "_buy_&_hold",
                stock_name + "_buy_&_hold",
            ]
        ],
        color_discrete_sequence=["green", "blue", "red"],
    )
    portfolio[stock2_name + "_SMA_daily_returns"] = portfolio[
        stock2_name + "_SMA_crossover"
    ].pct_change()

    mean_daily_return = portfolio[stock2_name + "_SMA_daily_returns"].mean()
    std_daily_return = portfolio[stock2_name + "_SMA_daily_returns"].std()
    stock_mean_daily_return = portfolio[stock_name + "_daily_return"].mean()
    daily_sharpe_ratio = (
        mean_daily_return - stock_mean_daily_return
    ) / std_daily_return

    annualized_sharpe_ratio = daily_sharpe_ratio * (trading_days ** 0.5)
    # return annualized_sharpe_ratio
    return (
        annualized_sharpe_ratio,
        cumulative_return_fig,
        SMA_fig,
        SMA_Crossovers_fig,
        strategy_performance_fig,
    )


if __name__ == "__main__":
    crypto_name = "ETH"
    stock_name = "BILI"
    
    alpaca, crypto_name, stock_name = backtest_set_up(API_KEY,API_SECRET,crypto_name,stock_name )
    stock_df = get_stock_df(alpaca,stock_name)
    stock2_df = get_stock_df(alpaca, "TSLA")
    crypto_df = get_crtpyo_df(alpaca,crypto_name)
    sharpe_ratio, cumulative_return_fig, SMA_fig, SMA_Crossovers_fig, strategy_performance_fig = SS_charts_n_sharp(stock_df,stock2_df, stock_name, "TSLA")
    # sharpe_ratio, cumulative_return_fig, SMA_fig, SMA_Crossovers_fig, strategy_performance_fig = CS_charts_n_sharp(stock_df,crypto_df, stock_name,crypto_name)
=======
    API_SECRET = "0GOzkmT1F5W9rs8czJ90YAXKZrBn6jee3BgGo9le"
    API_KEY = "PKNKABC4NQ6UURX5RU4R"
    BASE_URL = "https://paper-api.alpaca.markets"
    alpaca, crypto_name, stock_name = backtest_set_up(
        API_KEY, API_SECRET, crypto_name, stock_name
    )
    stock_df = get_stock_df(alpaca, stock_name)
    stock2_df = get_stock_df(alpaca, "TSLA")
    crypto_df = get_crtpyo_df(alpaca, crypto_name)
    # sharpe_ratio, cumulative_return_fig, SMA_fig, SMA_Crossovers_fig, strategy_performance_fig = SS_charts_n_sharp(stock_df,stock2_df, stock_name, "TSLA")
    (
        sharpe_ratio,
        cumulative_return_fig,
        SMA_fig,
        SMA_Crossovers_fig,
        strategy_performance_fig,
    ) = CS_charts_n_sharp(stock_df, crypto_df, stock_name, crypto_name)
