import streamlit.components.v1 as components  # Import Streamlit
import streamlit as st
""" 
--Liang created Apr 2 2023--
last update Apr 19 2023
""" 


"""
    Write an HTML file with the TradingView Widget for a given symbol.

    Args:
        symbol (str): The stock symbol to display in the TradingView Widget.

    Returns:
        None: The function writes the TradingView Widget HTML to 'currentstock.html'.
"""
def write_html_file(symbol):
  html = '''<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
    <div class="tradingview-widget-container__widget"></div>
    <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/NYSE-'''+symbol+'''/" rel="noopener" target="_blank"><span class="blue-text">'''+symbol+''' stock price</span></a> by TradingView</div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
    {
    "symbols": [
      [
        "a",
        "NYSE:'''+symbol+'''|1D"
      ]
    ],
    "chartOnly": false,
    "width": 1000,
    "height": 500,
    "locale": "en",
    "colorTheme": "light",
    "autosize": false,
    "showVolume": false,
    "showMA": false,
    "hideDateRanges": false,
    "hideMarketStatus": false,
    "hideSymbolLogo": false,
    "scalePosition": "right",
    "scaleMode": "Normal",
    "fontFamily": "-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif",
    "fontSize": "10",
    "noTimeScale": false,
    "valuesTracking": "1",
    "changeMode": "price-and-percent",
    "chartType": "area"
  }
    </script>
  </div>
  <!-- TradingView Widget END -->'''
  with open('src\candle\currentstock.html', 'w') as f:
      f.write(html)
"""
    Display the stock graph for a given symbol using Streamlit and a TradingView Widget.

    Args:
        symbol (str, optional): The stock symbol to display. Defaults to 'RTX'.
"""
def display_graph(symbol='RTX'):
  file_name = 'src/candle/currentstock.html'
  # Write the TradingView Widget HTML for the given symbol
  write_html_file(symbol)
  # Display a header in the Streamlit app
  st.header("test html import")
  # Read the contents of the generated HTML file
  HtmlFile = open(file_name, 'r', encoding='utf-8')
  source_code = HtmlFile.read()
  # Print the source code (for debugging purposes) 
  print(source_code)
  # Display the TradingView Widget in the Streamlit app using the components module
  components.html(source_code,width=1000, height=500)
  return source_code

# part = display_graph()
# components.html(part, header,descriotion)