# Live Market Price Tracker & Report Generator
import requests
from datetime import datetime

def fetch_crypto_prices():
    print("========================================")
    print("      LIVE CRYPTO MARKET TRACKER        ")
    print("========================================")
    print("Fetching live data from the web...\n")

    # Free public API for live market rates
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Extract prices and 24h change
        btc_price = data["bitcoin"]["usd"]
        btc_change = data["bitcoin"]["usd_24h_change"]

        eth_price = data["ethereum"]["usd"]
        eth_change = data["ethereum"]["usd_24h_change"]

        sol_price = data["solana"]["usd"]
        sol_change = data["solana"]["usd_24h_change"]

        # Get current time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format output
        report = []
        report.append("=" * 45)
        report.append(f"     MARKET REPORT ({now})")
        report.append("=" * 45)
        report.append(f"{'ASSET':<12} {'PRICE (USD)':<18} {'24H CHANGE':<12}")
        report.append("-" * 45)
        report.append(f"{'Bitcoin':<12} ${btc_price:<17,f} {btc_change:+.2f}%")
        report.append(f"{'Ethereum':<12} ${eth_price:<17,f} {eth_change:+.2f}%")
        report.append(f"{'Solana':<12} ${sol_price:<17,f} {sol_change:+.2f}%")
        report.append("=" * 45)

        full_report = "\n".join(report)
        print(full_report)

        # Automatically save to a log file
        with open("market_report.txt", "w", encoding="utf-8") as f:
            f.write(full_report)

        print("\n✅ Report successfully saved to: market_report.txt")

    except Exception as e:
        print("❌ Error fetching live data:", e)

# Run tracker
fetch_crypto_prices()