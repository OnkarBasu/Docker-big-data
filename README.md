# 📈 Stock Price Fetcher

A Python command-line tool that fetches real-time stock data using the Alpha Vantage API and prints a clean 7-day summary report in the terminal. The whole project is packaged into a Docker container so it runs the same way on any machine, anywhere.

---

## 📁 Project Structure

```
stockfetcher/
├── main.py            # Main Python script
├── requirements.txt   # Project dependencies
├── Dockerfile         # Instructions to build the Docker image
└── README.md          # This file
```

---

## 🧠 What It Does

You run the script and pass stock ticker symbols as arguments. For each ticker, it calls the Alpha Vantage API, grabs the last 7 days of price data, and prints a clean summary table in the terminal.

**For each stock you get:**
- Latest closing price
- 7-day high and low
- Average daily trading volume
- 7-day price change as a percentage

---

## 🐍 The Python Code (`main.py`)

The script has three functions. Here's each one with an explanation of what it does:

---

### 1. `fetch_stock_data(ticker)`

This is the core function. It calls the Alpha Vantage API for a given ticker, pulls the last 7 days of price data, and returns a dictionary of summary stats.

```python
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
```

The API returns a big JSON object. We sort the dates in reverse order so the most recent day comes first, then slice the first 7. From there we calculate the stats manually — max for the high, min for the low, average for volume, and a simple percentage formula for the price change.

If anything goes wrong (bad ticker, network issue, API limit), the `except` block catches it, prints an error, and returns `None` so the rest of the script keeps running.

---

### 2. `print_report(summaries)`

Takes the list of results and prints them as a formatted table with a timestamp.

```python
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
```

`tabulate` does the heavy lifting here — it automatically uses the dictionary keys as column headers and formats everything into a clean bordered table.

---

### 3. `main()`

The entry point. Reads tickers from the command line, loops through them, and ties everything together.

```python
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
        time.sleep(12)

    print_report(summaries)
```

`sys.argv[1:]` grabs everything typed after `python main.py`. The `.upper()` call means we can type `aapl` or `AAPL` and it works either way. The `time.sleep(12)` pause is there because Alpha Vantage's free tier only allows 5 requests per minute — without the pause it would hit the limit and fail.

---

## ⏱️ Why `time.sleep(12)`?

Alpha Vantage's free API key allows a maximum of 5 requests per minute. If you fire off requests back to back with no delay, it blocks you after the 5th one. Waiting 12 seconds between each ticker keeps us safely under that limit. It's a simple fix that makes the script reliable.

---

## 📦 Dependencies (`requirements.txt`)

```
requests==2.31.0
tabulate==0.9.0
```

| Library | What it does |
|---------|-------------|
| `requests` | Makes HTTP calls to the Alpha Vantage API |
| `tabulate` | Prints the results as a clean terminal table |

We switched from `yfinance` to Alpha Vantage because `yfinance` was blocking requests coming from Docker containers. Alpha Vantage works reliably everywhere.

---

## 🔑 API Key Setup

This project uses the [Alpha Vantage API](https://www.alphavantage.co/support/#api-key). We have generated a free API key in Vantage which will alloqw us to generate a stock summary report for past 7 days.

Once we have it, open `main.py` and replace this line at the top:
```python
API_KEY = "YOUR_API_KEY_HERE"
```

With your actual key:
```python
API_KEY = "ABC123XYZ"
```

---

## 🐳 Docker

### What is Docker?

Docker packages our app and all its dependencies into a container. It runs identically on any machine — no need to worry about Python versions or whether the other person has the right libraries installed.

- **Image** — the packaged blueprint of your app (built from the Dockerfile)
- **Container** — a running instance of that image
- **Dockerfile** — the instructions for building the image
- **Docker Hub** — a cloud registry where you store and share images publicly

---

### The Dockerfile

```dockerfile
# Start from an  lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY main.py .

# Default command if no tickers are passed
CMD ["python", "main.py", "AAPL"]
```

`requirements.txt` is copied and installed before `main.py` on purpose. Docker caches each step as a layer, so if we only change `main.py`, it skips reinstalling dependencies and rebuilds much faster.

---

## 🚀 How to Run It

### Locally (without Docker)

Install dependencies:
```bash
pip install -r requirements.txt
```

Run with any tickers you want:
```bash
python main.py AAPL TSLA GOOGL
```

---

### With Docker

**Build the image:**
```bash
docker build -t stock-fetcher .
```

**Run the container:**
```bash
docker run --rm stock-fetcher python main.py AAPL TSLA GOOGL
```

**Pull and run directly from Docker Hub:**
```bash
docker pull onkar45612/stock-fetcher:v2.0
docker run --rm onkar45612/stock-fetcher:v2.0 python main.py AAPL TSLA GOOGL
```

The `--rm` flag automatically deletes the container after it finishes running, keeping things clean.

---

## ☁️ Pushing to Docker Hub

```bash
# Log in to Docker Hub
docker login

# Tag the image with your Docker Hub username and version
docker tag stock-fetcher onkar45612/stock-fetcher:v2.0

# Push it
docker push onkar45612/stock-fetcher:v2.0
```

The `:v2.0` is a version label. We moved to v2.0 after switching from `yfinance` to Alpha Vantage. Both versions are available on Docker Hub.

---

## 🐳 Docker Hub

- **Latest image tag:** `onkar45612/stock-fetcher:v2.0`
- **Link:** https://hub.docker.com/r/onkar45612/stock-fetcher

---


