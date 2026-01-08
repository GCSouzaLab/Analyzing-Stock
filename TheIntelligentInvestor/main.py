import yfinance as yf
import streamlit as st
from yfinance import Ticker

def sub_header_analysis(name: str, sector: str):
    st.subheader(f"Analysis for {name} \n"
                 f"Sector: {sector}", divider="rainbow")

def header():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        ticker_symbol = st.text_input("Enter Company Ticker (e.g. AAPL, MSFT):", "AAPL")
    with col2:
        timeframe = st.selectbox("Time:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"])
    with col3:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        submitted = st.button("Analyse")

    return ticker_symbol, timeframe, submitted

def create_chart_price_history(ticker: Ticker, timeframe: str):
    st.write("Price History:")
    hist = ticker.history(period=timeframe)
    st.line_chart(hist['Close'])

def extract_basics_data(ticker: Ticker):
    name = ticker.info.get("longName")
    sector = ticker.info.get("sector")
    country = ticker.info.get("country")
    price = ticker.info.get("currentPrice")
    return name, price, sector, country

def dividend_yield(ticker: Ticker, price: int):
    currency = ticker.info.get("currency")
    st.metric(label="Current Price", value=f"{currency} {price}")

    # Focus on Dividend Yield
    col1, col2, col3 = st.columns(3)
    with col1:
        dividend_yield = ticker.info.get("dividendYield")
        st.write(f"Dividend Yield: {dividend_yield}%")
    with col2:
        last_dividend = round(ticker.info.get("lastDividendValue"), 2)
        st.write(f"Last Dividend Value: {last_dividend}")
    with col3:
        average_last5y_dividend = ticker.info.get("fiveYearAvgDividendYield")
        st.write(f"Average D.Y. Last 5y: {average_last5y_dividend}")

def compute_valuation(ticker_):
    metrics = {}
    # Current market price of one share.
    price = ticker_.get("currentPrice") or ticker_.get("regularMarketPrice")

    #P/VP or P/B
    metrics["p_to_book"] = ticker_.get("bookValue")

    # Trailing EPS = Net Income (last 12 months) / Shares Outstanding
    metrics["trailing_eps"] = ticker_.get("epsTrailingTwelveMonths") or ticker_.get("trailingEps")
    # Shows how much investors pay for past earnings
    metrics["pe_trailing"] = None if not price or not metrics["trailing_eps"] else price / metrics["trailing_eps"]

    # Reflects expected future earnings.
    eps_forward = ticker_.get("epsForward") or ticker_.get("forwardEps")
    metrics["pe_forward"] = None if not price or not eps_forward else price / eps_forward

    # Div. Yield - Annual dividend as a percentage of the current price.
    dividend_rate = ticker_.get("dividendRate") or ticker_.get("lastDividendValue")
    metrics["dividend_yield"] = None if not price or not dividend_rate else dividend_rate / price

    # Profitability / Growth
    metrics["roe"] = ticker_.get("returnOnEquity")
    # Short interest
    metrics["short_percent"] = ticker_.get("shortPercentOfFloat")
    return metrics

def score_signal(metrics2):
    """
      Score = Base + Valuation + Growth + Profitability + Income − Risk − Leverage
    """
    # Base 50 = neutral, not good, not bad...
    score = 50.0

    # Valuation: lower P/E adds score
    pe = metrics2.get("pe_forward") or metrics2.get("pe_trailing")
    if pe:
        if pe < 10: score += 15
        elif pe < 20: score += 8
        elif pe < 30: score += 3
        else: score -= 5

    # P/B
    pb = metrics2.get("p_to_book")
    if pb:
        if pb < 1: score += 10
        elif pb < 3: score += 3
        else: score -= 3

    # Dividend
    dy = metrics2.get("dividend_yield")
    if dy:
        if dy > 0.06: score += 8
        elif dy > 0.03: score += 3

    # Growth & profitability
    roe = metrics2.get("roe") or 0
    if roe and roe > 0.15: score += 5

    # Leverage risk
    de = metrics2.get("debtToEquity") or 0
    if de and de > 100: score -= 8

    # Short interest (high short interest reduces score)
    sp = metrics2.get("short_percent") or 0
    if sp > 0.05: score -= 6

    # Clamp
    score = max(0, min(100, score))

    # Map to label
    if score >= 90:
        label = ("STRONG BUY", "success")
    elif score >= 70:
        label = ("BUY", "success")
    elif score >= 45:
        label = ("HOLD", "warning")
    else:
        label = ("SELL", "error")
    return score, label

def describing_stock(symbol: str, timeframe: str, submitted: bool):
    if submitted:
        ticker = yf.Ticker(symbol)

        # Get basic info
        name, price, sector, country = extract_basics_data(ticker)

        sub_header_analysis(name, sector)

        dividend_yield(ticker, price)

        metrics = compute_valuation(ticker.info)

        # SIGNAL...
        score, (label, kind) = score_signal(metrics)
        if kind == "success":
            st.success(f"{label} — Score: {score:.0f}/100", width="50")
        elif kind == "warning":
            st.warning(f"{label} — Score: {score:.0f}/100")
        else:
            st.error(f"{label} — Score: {score:.0f}/100")

        st.caption("This is an automated signal. Not financial advice.")

        # Earnings & Valuation
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="P/VP",
                value=f"{round(metrics["p_to_book"], 2)}",
                help="Price-to-Book ratio. High values are normal for technology companies."
            )
        with col2:
            st.metric(
                label="Trailing EPS",
                value=f"{round(metrics["trailing_eps"], 2)}",
                help="Profit per share generated over the last 12 months."
            )
        with col3:
            st.metric(
                label="Forward EPS",
                value=f"{round(metrics["pe_forward"], 2)}",
                help="Expected profit per share for the next 12 months, based on analyst estimates."
            )

        st.divider()
        create_chart_price_history(ticker, timeframe)

def main():
    st.set_page_config(layout="wide", page_title="Stock Analyzer")
    symbol, timeframe, submitted = header()
    describing_stock(symbol, timeframe, submitted)

if __name__  == "__main__":
    main()

    info = yf.Ticker("ABEV3.SA").info
    print(info)
