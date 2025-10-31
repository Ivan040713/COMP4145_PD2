
# --- Import Streamlit FIRST ---
import streamlit as st
# --- Set Streamlit page config FIRST ---
# --- Set Streamlit page config FIRST ---
st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")
# --- List of tickers for user selection ---
SAMPLE_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'UNH',
    'HD', 'PG', 'MA', 'DIS', 'BAC', 'VZ', 'ADBE', 'CMCSA', 'NFLX', 'KO',
    'PFE', 'PEP', 'T', 'CSCO', 'ABT', 'CRM', 'XOM', 'WMT', 'CVX', 'MCD',
    'INTC', 'COST', 'NKE', 'LLY', 'TMO', 'MDT', 'DHR', 'WFC', 'ACN', 'AVGO',
    'QCOM', 'TXN', 'LIN', 'HON', 'UNP', 'NEE', 'PM', 'ORCL', 'IBM', 'AMGN',
    'SBUX', 'PYPL', 'GS', 'BA', 'GME', 'LMT', 'FDX', 'GE', 'CAT', 'BLK',
    'BKNG', 'DE', 'CL', 'HUM', 'AON', 'DUK', 'SO', 'MMM', 'SPGI', 'MS',
    'TGT', 'LOW', 'APD', 'ECL', 'F', 'GM', 'DAL', 'UAL', 'AAL', 'RCL',
    'C', 'USB', 'PNC', 'TFC', 'SCHW', 'ICE', 'CB', 'PGR', 'TRV', 'ALL',
    'AIG', 'MET', 'PRU', 'AFL', 'LNC', 'HIG', 'CINF', 'MKTX', 'NDAQ', 'CME',
    'Tencent Holdings Ltd', 'AIA Group Ltd', 'HSBC Holdings plc', 'China Construction Bank Corp', 'Ping An Insurance Group', 'Hong Kong Exchanges and Clearing Ltd', 'CNOOC Ltd', 'BOC Hong Kong Holdings Ltd', 'Hang Seng Bank Ltd', 'Galaxy Entertainment Group Ltd',
    'China Resources Power Holdings Co Ltd', 'China Overseas Land & Investment Ltd', 'WH Group Ltd', 'Geely Automobile Holdings Ltd', 'Sands China Ltd', 'Bank of East Asia Ltd', 'CITIC Ltd', 'HK Electric Investments Ltd', 'CK Hutchison Holdings Ltd', 'CLP Holdings Ltd'
]
HK_TICKER_MAP = {
    'Tencent Holdings Ltd': '0700.HK',
    'AIA Group Ltd': '1299.HK',
    'HSBC Holdings plc': '0005.HK',
    'China Construction Bank Corp': '0939.HK',
    'Ping An Insurance Group': '2318.HK',
    'Hong Kong Exchanges and Clearing Ltd': '0388.HK',
    'CNOOC Ltd': '0883.HK',
    'BOC Hong Kong Holdings Ltd': '2388.HK',
    'Hang Seng Bank Ltd': '0011.HK',
    'Galaxy Entertainment Group Ltd': '0027.HK',
    'China Resources Power Holdings Co Ltd': '0836.HK',
    'China Overseas Land & Investment Ltd': '0688.HK',
    'WH Group Ltd': '0288.HK',
    'Geely Automobile Holdings Ltd': '0175.HK',
    'Sands China Ltd': '1928.HK',
    'Bank of East Asia Ltd': '0233.HK',
    'CITIC Ltd': '0267.HK',
    'HK Electric Investments Ltd': '0282.HK',
    'CK Hutchison Holdings Ltd': '0001.HK',
    'CLP Holdings Ltd': '0002.HK'
}

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# --- Streamlit custom theme ---
st.markdown(
    '''<style>
    body, .reportview-container, .main, .block-container {
        background-color: #f0f4fa !important;
    }
    .stApp {
        background-color: #e3eafc !important;
    }
    .stMarkdown, .stTextInput, .stDataFrame, .stTable, .stTitle, .stHeader, .stSubheader, .stSelectbox label, .stRadio label {
        color: #1a237e !important;
    }
    .stButton>button {
        background-color: #1976d2 !important;
        color: #fff !important;
    }
    .stSidebar {
        background-color: #c5cae9 !important;
    }
    </style>''', unsafe_allow_html=True)

PAGES = [
    "Price Chart",
    "RSI",
    "Financials",
    "Statistics",
    "Analysis",
    "AI-Powered Investment Chatbot",
    "Formula teaching",
    "News Sentiment Analysis"
]

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", PAGES)

# --- Trading strategy functions (from trading_strategy.py) ---
def get_stock_data(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

def calculate_moving_averages(data):
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    return data

def identify_golden_cross(data):
    data['Signal'] = 0
    data['GoldenCross'] = (data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1))
    return data

def implement_strategy(data):
    positions = []
    data = data.iloc[200:].copy()
    buy_dates = data[data['GoldenCross'] == True].index.tolist()
    for buy_date in buy_dates:
        buy_price = data.loc[buy_date, 'Close']
        target_price = buy_price * 1.15
        max_sell_date = buy_date + pd.Timedelta(days=60)
        sell_period = data.loc[buy_date:max_sell_date].copy()
        target_reached = sell_period[sell_period['Close'] >= target_price]
        if not target_reached.empty:
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, 'Close']
            sell_reason = "Target reached"
        else:
            sell_date_candidates = sell_period.index.tolist()
            if sell_date_candidates:
                sell_date = sell_date_candidates[-1]
                sell_price = data.loc[sell_date, 'Close']
                sell_reason = "Max holding period"
            else:
                continue
        holding_days = (sell_date - buy_date).days
        profit_pct = (sell_price / buy_price - 1) * 100
        positions.append({
            'BuyDate': buy_date,
            'BuyPrice': buy_price,
            'SellDate': sell_date,
            'SellPrice': sell_price,
            'HoldingDays': holding_days,
            'ProfitPct': profit_pct,
            'SellReason': sell_reason
        })
    return pd.DataFrame(positions)

# --- Shared ticker selection for cross-page state ---
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = 'AAPL'

if page == "Price Chart":
    st.title("Price Chart")
    selected = st.selectbox("Select Stock", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state['selected_ticker']) if st.session_state['selected_ticker'] in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    ticker = HK_TICKER_MAP[selected] if selected in HK_TICKER_MAP else selected
    st.write(f"Fetching data for {selected}...")
    data = get_stock_data(ticker)
    if data.empty or 'Close' not in data:
        st.warning(f"No data found for {ticker}.")
    else:
        data = calculate_moving_averages(data)
        data = identify_golden_cross(data)
        positions = implement_strategy(data)
        # Reset index for plotting
        data = data.reset_index()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data["Date"], data["Close"], label="Close Price", color="blue")
        if "MA50" in data:
            ax.plot(data["Date"], data["MA50"], label="MA50", color="orange")
        if "MA200" in data:
            ax.plot(data["Date"], data["MA200"], label="MA200", color="green")
        # Plot buy/sell points
        if not positions.empty:
            for i, row in positions.iterrows():
                ax.scatter(row["BuyDate"], row["BuyPrice"], color="lime", marker="o", s=80, label="Buy" if i == 0 else "")
                ax.scatter(row["SellDate"], row["SellPrice"], color="red", marker="o", s=80, label="Sell" if i == 0 else "")
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_title(f"{ticker} Price Chart with MAs and Trades")
        st.pyplot(fig)
        st.subheader("Historical Data")
        st.dataframe(data)
        if not positions.empty:
            st.subheader("Trade Positions")
            st.dataframe(positions)
        else:
            st.info("No trades found for this ticker.")



elif page == "RSI":
    st.title("RSI")
    selected = st.selectbox("Select Stock for RSI", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    ticker = HK_TICKER_MAP[selected] if selected in HK_TICKER_MAP else selected
    st.write(f"Fetching RSI data for {selected}...")
    data = get_stock_data(ticker)
    if data.empty or 'Close' not in data:
        st.warning(f"No data found for {ticker}.")
    else:
        data = calculate_moving_averages(data)
        data = identify_golden_cross(data)
        positions = implement_strategy(data)
        # Calculate RSI
        from trading_strategy import calculate_rsi
        data = data.reset_index()
        data['RSI'] = calculate_rsi(data)
        # Price chart first
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data["Date"], data["Close"], label="Close Price", color="blue")
        if "MA50" in data:
            ax.plot(data["Date"], data["MA50"], label="MA50", color="orange")
        if "MA200" in data:
            ax.plot(data["Date"], data["MA200"], label="MA200", color="green")
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_title(f"{ticker} Price Chart with MAs")
        st.pyplot(fig)

        # RSI Graph
        fig_rsi, ax_rsi = plt.subplots(figsize=(12, 4))
        ax_rsi.plot(data['Date'], data['RSI'], label='RSI', color='purple')
        ax_rsi.axhline(70, color='red', linestyle='--', label='Overbought (70)')
        ax_rsi.axhline(30, color='green', linestyle='--', label='Oversold (30)')
        # Highlight overbought/oversold regions
        overbought = data[data['RSI'] > 70]
        oversold = data[data['RSI'] < 30]
        ax_rsi.scatter(overbought['Date'], overbought['RSI'], color='red', marker='^', s=60, label='Overbought')
        ax_rsi.scatter(oversold['Date'], oversold['RSI'], color='green', marker='v', s=60, label='Oversold')
        ax_rsi.set_title(f"RSI for {ticker}")
        ax_rsi.set_ylabel("RSI")
        ax_rsi.legend()
        st.pyplot(fig_rsi)
        # Show total times of overbought and oversold
        st.markdown(f"**Total Overbought (RSI>70):** {len(overbought)} times")
        st.markdown(f"**Total Oversold (RSI<30):** {len(oversold)} times")
        st.subheader("Historical Overbought Data")
        st.dataframe(overbought)
        st.subheader("Historical Oversold Data")
        st.dataframe(oversold)


elif page == "Financials":
    st.title("Financials")
    selected = st.selectbox("Select Stock for Financials", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    ticker = HK_TICKER_MAP[selected] if selected in HK_TICKER_MAP else selected
    stock = yf.Ticker(ticker)
    st.subheader(f"Income Statement for {ticker}")
    try:
        income = stock.financials
        if not income.empty:
            st.dataframe(income)
        else:
            st.info("No income statement data available.")
    except Exception as e:
        st.error(f"Error loading income statement: {e}")

    st.subheader(f"Balance Sheet for {ticker}")
    try:
        balance = stock.balance_sheet
        if not balance.empty:
            st.dataframe(balance)
        else:
            st.info("No balance sheet data available.")
    except Exception as e:
        st.error(f"Error loading balance sheet: {e}")

    st.subheader(f"Cash Flow for {ticker}")
    try:
        cashflow = stock.cashflow
        if not cashflow.empty:
            st.dataframe(cashflow)
        else:
            st.info("No cash flow data available.")
    except Exception as e:
        st.error(f"Error loading cash flow: {e}")
        
elif page == "Statistics":
    st.title("Statistics")
    selected = st.selectbox("Select Stock for Statistics", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    ticker = HK_TICKER_MAP[selected] if selected in HK_TICKER_MAP else selected
    stock = yf.Ticker(ticker)
    st.subheader(f"Key Statistics for {ticker}")
    try:
        info = stock.info
        if info:
            # Market Cap, Shares, Beta, PE, EPS, Forward Dividend, Ex-Dividend Date, etc.
            st.markdown("### Valuation Measures")
            valuation = {
                "Market Cap": info.get("marketCap"),
                "Enterprise Value": info.get("enterpriseValue"),
                "Trailing P/E": info.get("trailingPE"),
                "Forward P/E": info.get("forwardPE"),
                "PEG Ratio": info.get("pegRatio"),
                "Price/Sales": info.get("priceToSalesTrailing12Months"),
                "Price/Book": info.get("priceToBook"),
                "Enterprise Value/Revenue": info.get("enterpriseToRevenue"),
                "Enterprise Value/EBITDA": info.get("enterpriseToEbitda"),
            }
            st.table(pd.DataFrame(list(valuation.items()), columns=["Metric", "Value"]))

            st.markdown("### Financial Highlights")
            financial = {
                "Fiscal Year Ends": info.get("fiscalYearEnd"),
                "Most Recent Quarter": info.get("mostRecentQuarter"),
                "Profit Margin": info.get("profitMargins"),
                "Operating Margin": info.get("operatingMargins"),
                "Return on Assets": info.get("returnOnAssets"),
                "Return on Equity": info.get("returnOnEquity"),
                "Revenue": info.get("totalRevenue"),
                "Revenue Per Share": info.get("revenuePerShare"),
                "Quarterly Revenue Growth": info.get("revenueQuarterlyGrowth"),
                "Gross Profit": info.get("grossProfits"),
                "EBITDA": info.get("ebitda"),
                "Net Income": info.get("netIncomeToCommon"),
                "Diluted EPS": info.get("trailingEps"),
                "Quarterly Earnings Growth": info.get("earningsQuarterlyGrowth"),
            }
            st.table(pd.DataFrame(list(financial.items()), columns=["Metric", "Value"]))

            st.markdown("### Trading Information")
            trading = {
                "Shares Outstanding": info.get("sharesOutstanding"),
                "Float": info.get("floatShares"),
                "% Held by Insiders": info.get("heldPercentInsiders"),
                "% Held by Institutions": info.get("heldPercentInstitutions"),
                "Shares Short": info.get("sharesShort"),
                "Short Ratio": info.get("shortRatio"),
                "Short % of Float": info.get("shortPercentOfFloat"),
                "Beta": info.get("beta"),
                "52-Week Change": info.get("52WeekChange"),
                "S&P500 52-Week Change": info.get("SandP52WeekChange"),
                "52 Week High": info.get("fiftyTwoWeekHigh"),
                "52 Week Low": info.get("fiftyTwoWeekLow"),
                "50-Day Moving Average": info.get("fiftyDayAverage"),
                "200-Day Moving Average": info.get("twoHundredDayAverage"),
            }
            st.table(pd.DataFrame(list(trading.items()), columns=["Metric", "Value"]))

            st.markdown("### Dividend & Splits")
            dividend = {
                "Forward Annual Dividend Rate": info.get("dividendRate"),
                "Forward Annual Dividend Yield": info.get("dividendYield"),
                "Trailing Annual Dividend Rate": info.get("trailingAnnualDividendRate"),
                "Trailing Annual Dividend Yield": info.get("trailingAnnualDividendYield"),
                "5 Year Average Dividend Yield": info.get("fiveYearAvgDividendYield"),
                "Payout Ratio": info.get("payoutRatio"),
                "Dividend Date": info.get("dividendDate"),
                "Ex-Dividend Date": info.get("exDividendDate"),
                "Last Split Date": info.get("lastSplitDate"),
                "Last Split Factor": info.get("lastSplitFactor"),
            }
            st.table(pd.DataFrame(list(dividend.items()), columns=["Metric", "Value"]))
        else:
            st.info("No statistics data available.")
    except Exception as e:
        st.error(f"Error loading statistics: {e}")
        
elif page == "Analysis":
    st.title("Analysis")
    selected = st.selectbox("Select Stock for Analysis", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    ticker = HK_TICKER_MAP[selected] if selected in HK_TICKER_MAP else selected
    stock = yf.Ticker(ticker)
    st.subheader(f"Key Analysis for {ticker}")
    try:
        info = stock.info
        if info:
            # Earnings Estimates
            st.markdown("### Earnings Estimates")
            earnings = {
                "EPS (Current Year)": info.get("trailingEps"),
                "EPS (Next Year)": info.get("forwardEps"),
                "EPS (Next Quarter)": info.get("epsForward"),
                "EPS Growth (Next 5Y)": info.get("earningsGrowth"),
            }
            st.table(pd.DataFrame(list(earnings.items()), columns=["Metric", "Value"]))

            # Revenue Estimates
            st.markdown("### Revenue Estimates")
            revenue = {
                "Revenue (Current Year)": info.get("totalRevenue"),
                "Revenue Per Share": info.get("revenuePerShare"),
                "Quarterly Revenue Growth": info.get("revenueQuarterlyGrowth"),
            }
            st.table(pd.DataFrame(list(revenue.items()), columns=["Metric", "Value"]))

            # Growth Estimates
            st.markdown("### Growth Estimates")
            growth = {
                "Earnings Quarterly Growth": info.get("earningsQuarterlyGrowth"),
                "Revenue Quarterly Growth": info.get("revenueQuarterlyGrowth"),
                "EPS Growth (Past 5Y)": info.get("earningsQuarterlyGrowth"),
                "EPS Growth (Next 5Y)": info.get("earningsGrowth"),
            }
            st.table(pd.DataFrame(list(growth.items()), columns=["Metric", "Value"]))

            # Analyst Ratings
            st.markdown("### Analyst Ratings & Ratios")
            analyst = {
                "Beta": info.get("beta"),
                "Trailing P/E": info.get("trailingPE"),
                "Forward P/E": info.get("forwardPE"),
                "PEG Ratio": info.get("pegRatio"),
                "Price/Sales": info.get("priceToSalesTrailing12Months"),
                "Price/Book": info.get("priceToBook"),
                "Enterprise Value/Revenue": info.get("enterpriseToRevenue"),
                "Enterprise Value/EBITDA": info.get("enterpriseToEbitda"),
                "Profit Margin": info.get("profitMargins"),
                "Operating Margin": info.get("operatingMargins"),
                "Return on Assets": info.get("returnOnAssets"),
                "Return on Equity": info.get("returnOnEquity"),
            }
            st.table(pd.DataFrame(list(analyst.items()), columns=["Metric", "Value"]))
        else:
            st.info("No analysis data available.")
    except Exception as e:
        st.error(f"Error loading analysis: {e}")
    


if page == "AI-Powered Investment Chatbot":
    st.title("AI-Powered Investment Chatbot")
    st.markdown("""
    **AI-Powered Investment Chatbot**
    
    Enter a stock name (e.g., 'GOOGL') to get company background information.
    """)
    selected = st.selectbox("Select Stock for Chatbot", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    user_input = selected
    if user_input:
        import re
        from difflib import get_close_matches
        tickers_found = []
        # Check for tickers in the input (exact match)
        for t in SAMPLE_TICKERS:
            if re.search(rf'\b{t}\b', user_input, re.IGNORECASE):
                tickers_found.append(t)
        # Fuzzy match for ticker typos (e.g., APPL for AAPL)
        fuzzy_ticker = get_close_matches(user_input.upper(), SAMPLE_TICKERS, n=1, cutoff=0.8)
        for t in fuzzy_ticker:
            if t not in tickers_found:
                tickers_found.append(t)
        # Check for company names in the input
        company_map = {
            'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL', 'apple': 'AAPL', 'meta': 'META', 'facebook': 'META',
            'amazon': 'AMZN', 'tesla': 'TSLA', 'nvidia': 'NVDA', 'visa': 'V', 'unitedhealth': 'UNH', 'disney': 'DIS', 'netflix': 'NFLX',
            'coca-cola': 'KO', 'pepsi': 'PEP', 'intel': 'INTC', 'walmart': 'WMT', 'exxon': 'XOM', 'chevron': 'CVX', 'mcdonald': 'MCD',
            'starbucks': 'SBUX', 'ibm': 'IBM', 'oracle': 'ORCL', 'adobe': 'ADBE', 'paypal': 'PYPL', 'qualcomm': 'QCOM', 'costco': 'COST',
            'pfizer': 'PFE', 'procter': 'PG', 'gamestop': 'GME', 'boeing': 'BA', 'goldman': 'GS', 'jpmorgan': 'JPM', 'bank of america': 'BAC',
            'verizon': 'VZ', 'comcast': 'CMCSA', 'abbott': 'ABT', 'cisco': 'CSCO', 'lloyd': 'LLY', 'nike': 'NKE', 'honeywell': 'HON',
            'broadcom': 'AVGO', 'amgen': 'AMGN', 'lockheed': 'LMT', 'fedex': 'FDX', 'general electric': 'GE', 'caterpillar': 'CAT',
            'blackrock': 'BLK', 'booking': 'BKNG', 'deere': 'DE', 'colgate': 'CL', 'humana': 'HUM', 'aon': 'AON', 'duke': 'DUK', 'so': 'SO'
        }
        for name, tkr in company_map.items():
            if re.search(rf'\b{name}\b', user_input, re.IGNORECASE) and tkr in SAMPLE_TICKERS and tkr not in tickers_found:
                tickers_found.append(tkr)

        # Enhanced chatbot: buy/sell recommendations, reasons, price suggestions
        for ticker in tickers_found:
            # If ticker is a HK company name, map to ticker symbol
            yf_ticker = HK_TICKER_MAP[ticker] if ticker in HK_TICKER_MAP else ticker
            data = get_stock_data(yf_ticker)
            if data.empty or 'Close' not in data:
                st.warning(f"No data found for {ticker}.")
                continue
            data = calculate_moving_averages(data)
            data = identify_golden_cross(data)
            positions = implement_strategy(data)
            stock = yf.Ticker(yf_ticker)
            info = stock.info
            latest_price = data['Close'].iloc[-1]
            st.markdown(f"## {info.get('shortName', ticker)} ({ticker})")
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**Current stock price:** ${latest_price:,.2f}")
            col2.markdown(f"**52-low price:** ${info.get('fiftyTwoWeekLow', 'N/A'):,}")
            col3.markdown(f"**52-high price:** ${info.get('fiftyTwoWeekHigh', 'N/A'):,}")
            st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
            st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
            st.markdown(f"**Country:** {info.get('country', 'N/A')}")
            st.markdown(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
            st.markdown(f"**Description:** {info.get('longBusinessSummary', 'N/A')}")

            st.markdown("### Last 3 Years Financials")
            try:
                fin = stock.financials
                bal = stock.balance_sheet
                cash = stock.cashflow
                if not fin.empty and not bal.empty:
                    fin = fin.T.sort_index(ascending=False).head(3)
                    bal = bal.T.sort_index(ascending=False).head(3)
                    cash = cash.T.sort_index(ascending=False).head(3) if not cash.empty else None
                    for idx, row in fin.iterrows():
                        year = idx.year if hasattr(idx, 'year') else str(idx)
                        revenue = row.get('Total Revenue', 'N/A')
                        profit = row.get('Net Income', 'N/A')
                        total_sales = row.get('Total Revenue', 'N/A')
                        assets = bal.loc[idx].get('Total Assets', None) if idx in bal.index else None
                        equity = bal.loc[idx].get('Total Stockholder Equity', None) if idx in bal.index else None
                        roa = (profit / assets * 100) if profit and assets else None
                        roe = (profit / equity * 100) if profit and equity else None
                        total_cash = cash.loc[idx].get('Cash At End Of Period', None) if cash is not None and idx in cash.index else None
                        op_cash_flow = cash.loc[idx].get('Total Cash From Operating Activities', None) if cash is not None and idx in cash.index else None
                        pe_ratio = info.get('trailingPE', 'N/A')
                        pb_ratio = info.get('priceToBook', 'N/A')
                        debt_equity = info.get('debtToEquity', 'N/A')
                        eps = info.get('trailingEps', 'N/A')
                        irr = info.get('earningsQuarterlyGrowth', 'N/A')
                        sharpe = None
                        try:
                            hist = stock.history(period="3y")
                            if not hist.empty and 'Close' in hist:
                                returns = hist['Close'].pct_change().dropna()
                                sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else None
                        except:
                            pass
                        st.markdown(f"**Year:** {year}")
                        st.markdown(f"- Total Revenue: {revenue:,}" if revenue != 'N/A' else "- Total Revenue: N/A")
                        st.markdown(f"- Net Profit: {profit:,}" if profit != 'N/A' else "- Net Profit: N/A")
                        st.markdown(f"- Total Sales: {total_sales:,}" if total_sales != 'N/A' else "- Total Sales: N/A")
                        st.markdown(f"- ROA: {roa:.2f}%" if roa is not None else "- ROA: N/A")
                        st.markdown(f"- ROE: {roe:.2f}%" if roe is not None else "- ROE: N/A")
                        st.markdown(f"- Total Cash: {total_cash:,}" if total_cash is not None else "- Total Cash: N/A")
                        st.markdown(f"- Operating Cash Flow: {op_cash_flow:,}" if op_cash_flow is not None else "- Operating Cash Flow: N/A")
                        st.markdown(f"- Sharpe Ratio: {sharpe:.2f}" if sharpe is not None else "- Sharpe Ratio: N/A")
                        st.markdown(f"- price-to-earnings (P/E) ratio: {pe_ratio}")
                        st.markdown(f"- price-to-book (P/B) ratio: {pb_ratio}")
                        st.markdown(f"- debt-to-equity ratio: {debt_equity}")
                        st.markdown(f"- earnings per share (EPS): {eps}")
                        st.markdown(f"- IRR: {irr}")
                        st.markdown("---")
                else:
                    st.info("Financial data not available for this company.")
            except Exception as e:
                st.info(f"Could not fetch financials: {e}")

            # Recommendation subtitle
            st.subheader("Recommendation")
            # Data-driven reason for recommendation
            if not positions.empty:
                last_trade = positions.iloc[-1]
                last_profit = last_trade['ProfitPct']
                last_buy = last_trade['BuyPrice']
                last_sell = last_trade['SellPrice']
                current_price = latest_price
                reason = ""
                if last_profit > 0:
                    reason = f"The last trade yielded a profit of {last_profit:.2f}%. The sell price (${last_sell:.2f}) was higher than the buy price (${last_buy:.2f}). This suggests the strategy is currently effective, and it may be a good time to consider selling to lock in gains. Thank you."
                    st.success(f"SELL {ticker} (Last Profit: {last_profit:.2f}%)\nReason: {reason}")
                elif current_price < last_buy:
                    reason = f"The current price (${current_price:.2f}) is below the last buy price (${last_buy:.2f}), indicating a potential buying opportunity if you expect a rebound. Thank you."
                    st.warning(f"BUY {ticker} (Last Profit: {last_profit:.2f}%)\nReason: {reason}")
                else:
                    reason = f"No strong buy/sell signal. The last trade did not yield a profit, and the current price (${current_price:.2f}) is close to the last buy price (${last_buy:.2f}). Consider holding until a clearer signal emerges. Thank you."
                    st.info(f"HOLD {ticker}\nReason: {reason}")
            else:
                st.info("No trading signals detected to provide buy/sell recommendation.\nReason: The strategy did not generate any trades for this stock in the recent period. Consider reviewing technical and fundamental indicators before making a decision.")
        if not tickers_found:
            st.info("No valid stock ticker found in the input. Please try again with a different stock name or ticker symbol.")

elif page == "Formula teaching":
    st.title("Formula Teaching & Stock Analysis Guide")
    st.header("Basic Financial Terms & Formulas")
    st.markdown("""
**ROA (Return on Assets)**
- **Formula:** ROA = Net Income / Total Assets
- **Usage:** Measures how efficiently a company uses its assets to generate profit. Higher ROA means better asset efficiency.

**ROE (Return on Equity)**
- **Formula:** ROE = Net Income / Shareholder's Equity
- **Usage:** Indicates how well a company uses equity to generate profits. Higher ROE is generally better.

**RSI (Relative Strength Index)**
- **Formula:** RSI = 100 - [100 / (1 + RS)], where RS = Average Gain / Average Loss (over 14 periods)
- **Usage:** Technical indicator for momentum. RSI > 70: Overbought; RSI < 30: Oversold.
    """)

    st.header("Key Financial Statements")
    st.markdown("""
**Income Statement**
- Shows revenues, expenses, and profit over a period. Key for understanding profitability.

**Balance Sheet**
- Snapshot of assets, liabilities, and equity at a point in time. Reveals financial health and capital structure.

**Cash Flow Statement**
- Tracks cash inflows/outflows from operations, investing, and financing. Important for liquidity analysis.
    """)

    st.header("What Data to Check Before Buying a Stock?")
    st.markdown("""
1. **Profitability:**
    - Net Income, ROA, ROE
2. **Growth:**
    - Revenue/Earnings growth rates
3. **Valuation:**
    - P/E ratio, P/B ratio, PEG ratio
4. **Financial Health:**
    - Debt-to-equity, current ratio, cash flow
5. **Technical Indicators:**
    - RSI, moving averages, price trends
6. **Industry & News:**
    - Sector performance, recent news/events

**Tip:** Always compare these metrics to industry averages and historical values. Use multiple indicators for a balanced view.
    """)

elif page == "News Sentiment Analysis":
    st.title("News Sentiment Analysis")
    import requests
    import json  # For pretty-printing the response

    st.markdown("""
    This page fetches news sentiment data for a selected stock using the Alpha Vantage API.
    """)
    API_KEY = "2DNXP04IWOPYJD3E"
    # User selects ticker
    selected = st.selectbox("Select Stock for News Sentiment", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
    st.session_state['selected_ticker'] = selected
    ticker = HK_TICKER_MAP[selected] if selected in HK_TICKER_MAP else selected

    # Date input for news (default: yesterday)
    import datetime
    default_date = datetime.date.today() - datetime.timedelta(days=1)
    date_input = st.date_input("Select news start date", value=default_date)
    time_from = date_input.strftime("%Y%m%d") + "T0000"

    url = (
        "https://www.alphavantage.co/query?"
        "function=NEWS_SENTIMENT"
        f"&tickers={ticker}"
        f"&time_from={time_from}"
        "&limit=10"
        f"&apikey={API_KEY}"
    )

    st.write(f"Fetching news sentiment data for {ticker}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            st.subheader("Raw JSON Response")
            st.code(json.dumps(data, indent=4), language="json")
            # Optionally, display headlines and sentiment summary
            if "feed" in data:
                st.subheader("Top News Headlines & Sentiment")
                for item in data["feed"]:
                    st.markdown(f"**Headline:** {item.get('title', 'N/A')}")
                    st.markdown(f"- Source: {item.get('source', 'N/A')}")
                    st.markdown(f"- Published: {item.get('time_published', 'N/A')}")
                    st.markdown(f"- Sentiment: {item.get('overall_sentiment_label', 'N/A')}")
                    st.markdown(f"- Summary: {item.get('summary', 'N/A')}")
                    st.markdown("---")
            else:
                st.info("No news feed data found in response.")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception occurred while fetching news sentiment: {e}")
