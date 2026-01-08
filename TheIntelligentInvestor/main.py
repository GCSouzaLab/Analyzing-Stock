from typing import Any

import yfinance as yf
import streamlit as st
from yfinance import Ticker

def search_button():
    ticker_symbol = st.text_input("Enter Company Ticker (e.g. AAPL, MSFT):", "AAPL")
    return ticker_symbol

def create_chart_price_history(ticker: Ticker):
    st.write("Price History:")
    hist = ticker.history(period="1y")
    st.line_chart(hist['Close'])

def extract_basics_data(ticker: Ticker):
    name = ticker.info.get("longName")
    sector = ticker.info.get("sector")
    country = ticker.info.get("country")
    price = ticker.info.get("currentPrice")
    return name, price, sector, country

def desc_stock(symbol):
    if st.button("Analyse"):
        ticker = yf.Ticker(symbol)

        # Get basic info
        name, price, sector, country = extract_basics_data(ticker)

        sub_header_analysis(name, sector)

        metrics(ticker, price)

        create_chart_price_history(ticker)


def metrics(ticker: Any | None, price: Any | None):
    currency = ticker.info.get("currency")
    st.metric(label="Current Price", value=f"{currency} {price}")

    col1, col2, col3 = st.columns(3)
    with col1:
        dividend_yield = ticker.info.get("dividendYield")
        st.write(f"Dividend Yield: % {dividend_yield}")
    with col2:
        last_dividend = ticker.info.get("lastDividendValue")
        st.write(f"Last Dividend Value: {last_dividend}")
    with col3:
        average_last5y_dividend = ticker.info.get("fiveYearAvgDividendYield")
        st.write(f"Average last 5y: {average_last5y_dividend}")

def sub_header_analysis(name: Any | None, sector: Any | None):
    st.subheader(f"Analysis for {name} \n"
                 f"Sector: {sector}", divider="rainbow")

def main():
    symbol = search_button()
    desc_stock(symbol)

if __name__  == "__main__":
    main()