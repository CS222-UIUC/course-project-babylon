# CS222_Automated Stocks Trading Bot
## Summary
This project proposes the creation of an Automated Crypto Trading Bot that will use a trading algorithm designed in Python to make trades based on market data. The bot will connect to the Alpaca API to gather the necessary data and make trades on behalf of the user. The results of the trades will be displayed on a web interface designed using Streamlit for users to monitor the performance of the bots.
## Technical Architecture
- Main App: The entry point of your application where the API keys and other configurations are set.
- API Class: This class handles the login and logout process and provides functions to manage the trading bot.
- Execution Class: This class is responsible for creating and managing instances of the trading bot, as well as handling trading activities.
- Events Class: This class handles log-related tasks, such as displaying and deleting logs.
- BOT Class: The core trading bot class that implements the trading strategy, interacts with the Alpaca API, and performs trading operations.
- Alpaca API: The Alpaca trading platform API that your application interacts with to fetch market data, submit orders, and manage positions.
- TA-Lib: A technical analysis library used for calculating RSI (Relative Strength Index) values.
- Logging Module: A module for logging messages and events related to the trading bot's activities.
- Data Storage: Represents the storage for log data.
- Graph: Present real-time interactive stock trends.
- Web Interface: Construct with Streamlit API, intergrating all needed functionalities from the backend and making them user usable.
## Installation Instruction
- Clone this repository into your machine with appropriate python environment installed
- Install all required packages with `pip install -r ./src/candle/requirement.txt`
- Follow the instruction to install [Ta-Lib](https://pypi.org/project/TA-Lib/)
- To run the application: `python3 -m streamlit run .\src\web\st_gui.py` or `streamlit run .\src\web\st_gui.py`
## Group Members
- Tass Hu: working on most of the backend part, including the algorithm of trading bot, Alpaca API connections, and provide supportive functionalities to the frontend
- Chaoxiong Liang: working on Alpaca API connections, making real-time, interactive graphs based on data gathered
- Jingyan Hu: working on the web interface, integrating functionalities that user will access to
- Xinyi Ye: working on the web interface, integrating functionalities that user will access to
