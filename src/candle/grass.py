import streamlit.components.v1 as components  # Import Streamlit
import streamlit as st


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

def display_graph(symbol):
  file_name = 'currentstock.html'
  write_html_file(symbol)
  # st.header("test html import")
  HtmlFile = open('src\candle\currentstock.html', 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  # print(source_code)
  components.html(source_code,width=1000, height=500)
  return source_code

# part = display_graph()
# components.html(part, header,descriotion)