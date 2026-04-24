import yfinance as yf
import pandas as pd
from tabulate import tabulate
from datetime import datetime,timedelta
import sys
import traceback
import time


def fetch_stock_data(ticker: str) ->dict:
    try:
        
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days = 7)
        history = stock.history(start=start_date, end=end_date, auto_adjust=True)
        if isinstance(history.columns, pd.MultiIndex):
            history.columns = history.columns.get_level_values(0)
        print(f"[DEBUG] Rows fetched for {ticker}: {len(history)}")

        if history.empty:

            print(f"no data found {ticker}")
            return None
        
        #summary stats
        latest_close = round(history["Close"].iloc[-1],2)
        week_high = round(history["High"].max(),2)
        week_low = round(history["Low"].min(),2)
        avg_volume = int(history["Volume"].mean())
        price_change = round(
            ((history["Close"].iloc[-1] - history["Close"].iloc[0]) 
            / history["Close"].iloc[0]) * 100, 2
        )

        return{
            "Ticker":ticker,
            "Latest_Close":latest_close,
            "7 day high($)": week_high,
            "7 day low($)": week_low,
            "Avg Volume": avg_volume,
            "7 Day Change(%)": price_change

        }
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {ticker}: {e}")
        traceback.print_exc()
        return None


def print_report(summaries: list ) -> None:
    """Print a formatted summary table to the terminal."""
    if not summaries:
        print("No data to display.")
        return

    print("\n" + "=" * 60)
    print("       📈 STOCK PRICE SUMMARY REPORT")
    print(f"       Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    print(tabulate(summaries, headers="keys", tablefmt="fancy_grid"))

    print("\n" + "=" * 60 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py AAPL TSLA GOOGL")
        print("Please provide at least one ticker symbol.")
        sys.exit(1)

    tickers = [ticker.upper() for ticker in sys.argv[1:]]
    print(f"\nFetching data for: {', '.join(tickers)}...")
    summaries = []
    for ticker in tickers:
        data = fetch_stock_data(ticker)
        if data:
            summaries.append(data)
        time.sleep(4)

    print_report(summaries)


if __name__ == "__main__":
    main()

    
