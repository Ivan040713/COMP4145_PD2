
# --- List of tickers for user selection ---
SAMPLE_TICKERS = [
	'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'UNH',
	'HD', 'PG', 'MA', 'DIS', 'BAC', 'VZ', 'ADBE', 'CMCSA', 'NFLX', 'KO',
	'PFE', 'PEP', 'T', 'CSCO', 'ABT', 'CRM', 'XOM', 'WMT', 'CVX', 'MCD',
	'INTC', 'COST', 'NKE', 'LLY', 'TMO', 'MDT', 'DHR', 'WFC', 'ACN', 'AVGO',
	'QCOM', 'TXN', 'LIN', 'HON', 'UNP', 'NEE', 'PM', 'ORCL', 'IBM', 'AMGN'
]

import streamlit as st
import pandas as pd
import numpy as np

import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")

PAGES = [
	"Price Chart",
	"Portfolio Analysis",
	"News & Sentiment",
	"Financials",
	"AI-Powered Investment Chatbot"
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
	ticker = st.selectbox("Select Stock", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state['selected_ticker']) if st.session_state['selected_ticker'] in SAMPLE_TICKERS else 0)
	st.session_state['selected_ticker'] = ticker
	st.write(f"Fetching data for {ticker}...")
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




elif page == "Portfolio Analysis":
	st.title("Portfolio Analysis")
	ticker = st.selectbox("Select Stock for Portfolio Analysis", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
	st.session_state['selected_ticker'] = ticker
	st.subheader(f"Portfolio Analysis for {ticker}")
	data = get_stock_data(ticker)
	if data.empty or 'Close' not in data:
		st.warning(f"No data found for {ticker}.")
	else:
		data = calculate_moving_averages(data)
		data = identify_golden_cross(data)
		positions = implement_strategy(data)
		# Simulate portfolio value (cumulative returns from trades)
		portfolio = pd.DataFrame()
		if not positions.empty:
			# Assume starting capital $10,000, invest full capital in each trade sequentially
			capital = 10000
			values = []
			dates = []
			returns = []
			for _, row in positions.iterrows():
				ret = (row['SellPrice'] / row['BuyPrice']) - 1
				capital = capital * (1 + ret)
				values.append(capital)
				dates.append(row['SellDate'])
				returns.append(ret)
			portfolio['Date'] = dates
			portfolio['PortfolioValue'] = values
			portfolio['TradeReturn'] = returns
			st.line_chart(portfolio.set_index('Date'))
			st.write("**Simulated portfolio value over time (sequential trades, $10,000 start):**")
			st.dataframe(portfolio)

			# Performance measurement
			st.markdown("### Performance Measurement")
			total_return = (values[-1] / 10000 - 1) * 100 if values else 0
			avg_return = np.mean(returns) * 100 if returns else 0
			st.write(f"Total Return: {total_return:.2f}%")
			st.write(f"Average Trade Return: {avg_return:.2f}%")
			st.write(f"Number of Trades: {len(returns)}")

			# Risk assessment
			st.markdown("### Risk Assessment")
			volatility = np.std(returns) * 100 if returns else 0
			st.write(f"Trade Return Volatility: {volatility:.2f}%")
			# Simple stress test: what if last trade was -20%?
			stress_test = capital * 0.8
			st.write(f"Stress Test (last trade -20%): Portfolio Value = ${stress_test:,.2f}")

			# Asset allocation analysis (single stock, so 100%)
			st.markdown("### Asset Allocation Analysis")
			st.write(f"All capital allocated to {ticker}.")

			# Risk-reward optimization (placeholder)
			st.markdown("### Risk-Reward Optimization")
			st.write("For a real portfolio, this would suggest rebalancing or diversification. Here, consider adding more stocks for lower risk.")

			# Scenario analysis (placeholder)
			st.markdown("### Scenario Analysis")
			st.write("Explore what-if scenarios by changing the stock or strategy parameters.")
		else:
			st.info("No trades found for this ticker.")



elif page == "News & Sentiment":
	st.title("News & Sentiment Integration")
	ticker = st.selectbox("Select Stock for News", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
	st.session_state['selected_ticker'] = ticker
	st.markdown(f"**Latest News for {ticker}**")
	try:
		stock = yf.Ticker(ticker)
		news = stock.news if hasattr(stock, 'news') else []
		if news:
			for item in news[:10]:
				title = item.get('title', 'No Title')
				link = item.get('link', '#')
				publisher = item.get('publisher', '')
				st.markdown(f"- [{title}]({link})  ")
				if publisher:
					st.caption(f"Source: {publisher}")
		else:
			st.info("No news found for this ticker.")
	except Exception as e:
		st.error(f"Error fetching news: {e}")
	st.markdown("""
	---
	This page shows recent news headlines and sentiment analysis for selected stocks, helping you stay informed about market-moving events.
	""")

elif page == "Financials":
	st.title("Financials")
	ticker = st.selectbox("Select Stock for Financials", SAMPLE_TICKERS, index=SAMPLE_TICKERS.index(st.session_state.get('selected_ticker', 'AAPL')) if st.session_state.get('selected_ticker', 'AAPL') in SAMPLE_TICKERS else 0)
	st.session_state['selected_ticker'] = ticker
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
	



if page == "AI-Powered Investment Chatbot":
	st.title("AI-Powered Investment Chatbot")
	st.markdown("""
	**AI-Powered Investment Chatbot**
    
	Ask about a stock (e.g., 'Tell me about GOOGL') to get company background information.
	""")
	user_input = st.text_input("Ask a question about a stock:", "E.g. Tell me about GOOGLE")
	if user_input:
		import re
		# Try to extract all tickers or company names from the input
		tickers_found = []
		# Check for tickers in the input
		for t in SAMPLE_TICKERS:
			if re.search(rf'\b{t}\b', user_input, re.IGNORECASE):
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
		if tickers_found:
			for ticker in tickers_found:
				try:
					stock = yf.Ticker(ticker)
					info = stock.info
					st.markdown(f"### {info.get('shortName', ticker)} ({ticker})")
					st.write(f"**Industry:** {info.get('industry', 'N/A')}")
					st.write(f"**Sector:** {info.get('sector', 'N/A')}")
					st.write(f"**Founded:** {info.get('founded', info.get('startDate', 'N/A'))}")
					st.write(f"**Country:** {info.get('country', 'N/A')}")
					st.write(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
					st.write(f"**Description:** {info.get('longBusinessSummary', 'N/A')}")

					# Try to get financials for last 3 years
					try:
						fin = stock.financials
						bal = stock.balance_sheet
						if not fin.empty and not bal.empty:
							fin = fin.T.sort_index(ascending=False).head(3)
							bal = bal.T.sort_index(ascending=False).head(3)
							st.markdown("#### Last 3 Years Financials")
							for idx, row in fin.iterrows():
								year = idx.year if hasattr(idx, 'year') else str(idx)
								revenue = row.get('Total Revenue', 'N/A')
								profit = row.get('Net Income', 'N/A')
								assets = bal.loc[idx].get('Total Assets', None) if idx in bal.index else None
								equity = bal.loc[idx].get('Total Stockholder Equity', None) if idx in bal.index else None
								roa = (profit / assets * 100) if profit and assets else None
								roe = (profit / equity * 100) if profit and equity else None
								st.write(f"**Year:** {year}")
								st.write(f"- Total Revenue: {revenue:,.0f}" if revenue != 'N/A' else "- Total Revenue: N/A")
								st.write(f"- Net Profit: {profit:,.0f}" if profit != 'N/A' else "- Net Profit: N/A")
								st.write(f"- ROA: {roa:.2f}%" if roa is not None else "- ROA: N/A")
								st.write(f"- ROE: {roe:.2f}%" if roe is not None else "- ROE: N/A")
								st.write("")
						else:
							st.info("Financial data not available for this company.")
					except Exception as e:
						st.info(f"Could not fetch financials: {e}")

					# Sharpe ratio (simple, based on 3y price history)
					try:
						hist = stock.history(period="3y")
						if not hist.empty and 'Close' in hist:
							returns = hist['Close'].pct_change().dropna()
							sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else None
							st.write(f"**3-Year Sharpe Ratio:** {sharpe:.2f}" if sharpe is not None else "**3-Year Sharpe Ratio:** N/A")
						else:
							st.write("**3-Year Sharpe Ratio:** N/A")
					except Exception as e:
						st.info(f"Could not calculate Sharpe ratio: {e}")

				except Exception as e:
					st.error(f"Could not fetch company info for {ticker}: {e}")
		else:
			st.info("Please ask about a valid stock ticker or company name (e.g., 'Tell me about GOOGL or Microsoft').")
