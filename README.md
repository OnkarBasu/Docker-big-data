#  Stock Price Fetcher

A Python command-line tool that pulls real-time stock data from Yahoo Finance and prints a clean 7-day summary report in the terminal. The whole thing is packaged into a Docker container so it runs the same way on any machine.

---

##  Project Structure

```
stockfetcher/
├── main.py            # Main Python script
├── requirements.txt   # Project dependencies
├── Dockerfile         # Instructions to build the Docker image
└── README.md          # This file
```

---

##  What It Does

You pass stock ticker symbols as arguments when running the script. For each ticker, it fetches the last 7 days of historical price data from Yahoo Finance, calculates some useful stats, and prints everything in a neat table.

**For each stock you get:**
- Latest closing price
- 7-day high and low
- Average daily trading volume
- 7-day price change as a percentage

---

##  The Python Code (`main.py`)

The script is split into three functions:

**`fetch_stock_data(ticker)`**
 It uses `yfinance` to pull 7 days of historical data for a given ticker, then calculates the summary stats. If anything goes wrong (bad ticker, network issue, rate limit), it catches the error, prints a message, and moves on without crashing.

**`print_report(summaries)`**
Takes all the results and prints them as a formatted table using `tabulate`. Also shows the exact time the report was generated.

**`main()`**
Reads the tickers from the command line using `sys.argv`, loops through each one, calls `fetch_stock_data()`, and passes all results to `print_report()`. There's a `time.sleep(4)` between each ticker to avoid hitting Yahoo Finance's rate limit.

---

## ⏱️ Why `time.sleep(4)`?

Yahoo Finance limits how many requests you can make in a short period. If you fetch too many tickers back to back without any pause, it blocks you temporarily with a `Too Many Requests` error. Adding a 4 second wait between each ticker keeps things slow enough to stay under the limit. It's a simple and effective fix.

---

##  Dependencies (`requirements.txt`)

```
yfinance==0.2.61
pandas==2.2.2
tabulate==0.9.0


## 🐳 Docker

### What is Docker?
Docker lets you package your app and all its dependencies into a container. The container runs the same way on any machine — no need to worry about Python versions or missing libraries on someone else's computer.

- **Image** — the packaged blueprint of your app (built from the Dockerfile)
- **Container** — a running instance of that image
- **Dockerfile** — a file with step-by-step instructions for building the image
- **Docker Hub** — a cloud registry where you store and share images

---

### The Dockerfile

```dockerfile
# Start from an official slim Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY main.py .

# Default command if no tickers are provided
CMD ["python", "main.py", "AAPL"]
```

One thing worth noting — `requirements.txt` is copied and installed before `main.py`. This is intentional. Docker builds in layers and caches them, so if you only change `main.py`, Docker skips reinstalling all the dependencies and rebuilds much faster.

---

## 🚀 How to Run It

### Locally (without Docker)

Install the dependencies:
```bash
pip install -r requirements.txt
```

Run the script with your chosen tickers:
```bash
python main.py AAPL TSLA GOOGL MSFT AMZN
```

---

### With Docker

**Build the image:**
```bash
docker build -t stock-fetcher .
```

**Run the container:**
```bash
docker run --rm stock-fetcher python main.py AAPL TSLA GOOGL MSFT AMZN
```

`--rm` just means the container gets deleted automatically after it finishes running, keeping things clean.

**Pull and run directly from Docker Hub:**
```bash
docker pull onkar45612/stock-fetcher:v1.0
docker run --rm onkar45612/stock-fetcher:v1.0 python main.py AAPL TSLA GOOGL MSFT AMZN
```

---

## ☁️ Pushing to Docker Hub

Docker Hub is where the image lives so anyone can pull and run it without needing the source code.

```bash
# Log in to Docker Hub
docker login

# Tag the image with your Docker Hub username
docker tag stock-fetcher onkar45612/stock-fetcher:v1.0

# Push it
docker push onkar45612/stock-fetcher:v1.0
```

The tag `v1.0` is just a version label. Without a tag Docker defaults to `latest`.

---

## 🐳 Docker Hub

- **Image tag:** `onkar45612/stock-fetcher:v1.0`
- **Link:** https://hub.docker.com/r/onkar45612/stock-fetcher

---

## 🛠️ Useful Docker Commands

| Command | What it does |
|---------|-------------|
| `docker build -t name .` | Build an image from the Dockerfile |
| `docker run --rm name` | Run a container and delete it after it exits |
| `docker images` | List all images on your machine |
| `docker ps -a` | List all containers including stopped ones |
| `docker logs <container>` | See what a container printed |
| `docker rmi name` | Delete an image |
| `docker system prune` | Clean up unused images and containers |
| `docker login` | Log in to Docker Hub |
| `docker tag name user/name:v1.0` | Tag an image for Docker Hub |
| `docker push user/name:v1.0` | Upload image to Docker Hub |
| `docker pull user/name:v1.0` | Download image from Docker Hub |
