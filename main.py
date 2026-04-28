import requests
import sys
import time
from datetime import datetime
from tabulate import tabulate


API_KEY = "UELM59JU1DJUDNN6"  # Replace with your actual key


def fetch_stock_data(ticker: str) -> dict:
    """Fetch 7-day summary for a stock using Alpha Vantage API."""
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",
            "apikey": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "Time Series (Daily)" not in data:
            print(f"[!] No data found for {ticker}. Response: {data}")
            return None

        time_series = data["Time Series (Daily)"]

        # Get last 7 days of data
        dates = sorted(time_series.keys(), reverse=True)[:7]

        closes = [float(time_series[d]["4. close"]) for d in dates]
        highs = [float(time_series[d]["2. high"]) for d in dates]
        lows = [float(time_series[d]["3. low"]) for d in dates]
        volumes = [int(time_series[d]["5. volume"]) for d in dates]

        latest_close = round(closes[0], 2)
        week_high = round(max(highs), 2)
        week_low = round(min(lows), 2)
        avg_volume = int(sum(volumes) / len(volumes))
        price_change = round(((closes[0] - closes[-1]) / closes[-1]) * 100, 2)

        return {
            "Ticker": ticker,
            "Latest Close ($)": latest_close,
            "7D High ($)": week_high,
            "7D Low ($)": week_low,
            "Avg Volume": avg_volume,
            "7D Change (%)": price_change
        }

    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {ticker}: {e}")
        return None


def print_report(summaries: list) -> None:
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
        time.sleep(12)  # Alpha Vantage free tier: 5 requests per minute

    print_report(summaries)


if __name__ == "__main__":
    main()
