def calculate_rsi(data, period=14):
    close = data['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
import pandas as pd
import numpy as np
import yfinance as yf
import random
from datetime import datetime, timedelta

# Download 5 years of data for a ticker
def get_stock_data(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

# Calculate moving averages
def calculate_moving_averages(data):
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    return data

# Identify golden cross (buy signals)
def identify_golden_cross(data):
    data['Signal'] = 0  # Initialize signal column with 0
    # Golden Cross occurs when MA50 crosses above MA200
    data['GoldenCross'] = (data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1))
    return data

# Implement trading strategy
def implement_strategy(data):
    positions = []

    # Need at least 200 days to calculate the 200-day MA
    data = data.iloc[200:].copy()

    buy_dates = data[data['GoldenCross'] == True].index.tolist()

    for buy_date in buy_dates:
        # Get buy price
        buy_price = data.loc[buy_date, 'Close']

        # Calculate target sell price (15% profit)
        target_price = buy_price * 1.15

        # Set maximum holding period
        max_sell_date = buy_date + pd.Timedelta(days=60)

        # Get data slice for potential sell period
        sell_period = data.loc[buy_date:max_sell_date].copy()

        # Check if target price is reached during the period
        target_reached = sell_period[sell_period['Close'] >= target_price]

        if not target_reached.empty:
            # Sell at first date target is reached
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, 'Close']
            sell_reason = "Target reached"
        else:
            # Sell at end of maximum holding period
            sell_date_candidates = sell_period.index.tolist()
            if sell_date_candidates:
                sell_date = sell_date_candidates[-1]
                sell_price = data.loc[sell_date, 'Close']
                sell_reason = "Max holding period"
            else:
                # Skip if no valid sell date (should not happen in practice)
                continue

        # Calculate holding period in calendar days
        holding_days = (sell_date - buy_date).days

        # Calculate profit
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

# Analyze the results
def analyze_results(positions):
    if positions.empty:
        return "No trading signals detected"

    # Summary statistics
    total_trades = len(positions)
    win_trades = len(positions[positions['ProfitPct'] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0

    avg_profit = positions['ProfitPct'].mean()
    avg_win = positions[positions['ProfitPct'] > 0]['ProfitPct'].mean() if win_trades > 0 else 0
    avg_loss = positions[positions['ProfitPct'] <= 0]['ProfitPct'].mean() if loss_trades > 0 else 0

    avg_holding = positions['HoldingDays'].mean()

    target_reached = len(positions[positions['SellReason'] == 'Target reached'])
    max_period = len(positions[positions['SellReason'] == 'Max holding period'])

    print("\n===== Trading Strategy Results (Golden Cross)=====")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {win_trades} ({win_rate:.2f}%)")
    print(f"Losing Trades: {loss_trades}")
    print(f"Average Profit: {avg_profit:.2f}%")

    return positions

# List of possible stock tickers (S&P 500 sample, can be expanded)
SAMPLE_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'UNH',
    'HD', 'PG', 'MA', 'DIS', 'BAC', 'VZ', 'ADBE', 'CMCSA', 'NFLX', 'KO',
    'PFE', 'PEP', 'T', 'CSCO', 'ABT', 'CRM', 'XOM', 'WMT', 'CVX', 'MCD',
    'INTC', 'COST', 'NKE', 'LLY', 'TMO', 'MDT', 'DHR', 'WFC', 'ACN', 'AVGO',
    'QCOM', 'TXN', 'LIN', 'HON', 'UNP', 'NEE', 'PM', 'ORCL', 'IBM', 'AMGN',
    'SBUX', 'LOW', 'MS', 'GS', 'BLK', 'AXP', 'BA', 'GE', 'CAT', 'MMM',
    'SPGI', 'PLD', 'ISRG', 'SYK', 'ZTS', 'GILD', 'MDLZ', 'AMT', 'CB', 'USB',
    'TGT', 'BKNG', 'DE', 'C', 'LMT', 'ADP', 'NOW', 'MO', 'EL', 'FIS',
    'SO', 'DUK', 'AON', 'CCI', 'CL', 'APD', 'SHW', 'ITW', 'MMC', 'FDX',
    'GM', 'EMR', 'ECL', 'PSA', 'AIG', 'AEP', 'ALL', 'TFC', 'HUM', 'AFL'
]

def main():
    # Randomly select 20 unique tickers
    tickers = random.sample(SAMPLE_TICKERS, 20)
    all_positions = {}

    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        data = get_stock_data(ticker)
        if data.empty or 'Close' not in data:
            print(f"No data for {ticker}, skipping.")
            continue
        data = calculate_moving_averages(data)
        data = identify_golden_cross(data)
        positions = implement_strategy(data)
        analyze_results(positions)
        all_positions[ticker] = positions

    return all_positions

all_positions = main()
print("\nDetailed Trades for all stocks:")
for ticker, positions in all_positions.items():
    print(f"\n{ticker}:")
    if positions.empty:
        print("No trades.")
    else:
        print(positions.to_string())
