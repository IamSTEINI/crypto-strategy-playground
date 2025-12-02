import requests
import os
import pandas as pd
import time
from datetime import datetime
import csv

# In this script I want to fetch all chart data, if that data is fetched I want it to stay updated
# By checking if the data exists and if there is a date (getting the last line timestamp) and choosing a startTime

symbols = ["ETH", "BTC", "SOL", "XRP", "SUI"]
intervals = ["1w", "1d", "12h", "4h", "1h", "30m", "15m", "5m", "1m"]
pair = "USDT"
base_path = "CSP"
url = "https://api.binance.com/api/v3/klines"
session = requests.Session()


# Checking if the folder exists
for symbol in symbols:
    if not os.path.exists(os.path.join(base_path,symbol)):
        os.makedirs(os.path.join(base_path,symbol))

# Fetching all the symbol data
def fetch_symbol_data(symbol, interval, end_time_ms, start_time=None):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 1000,
        "endTime": end_time_ms,
    }
    if start_time:
        params["startTime"] = start_time
    r = session.get(url, params=params)
    data = r.json()
    if not data or isinstance(data, dict):
        return None
    return data

def fetch_symbol(symbol, interval_index):
    end_time = int(datetime.now().timestamp() * 1000)
    first_write = True
    batch = 1
    if not interval_index > len(intervals):
        interval = intervals[interval_index]
        file_path = f"{base_path}/{str(symbol).replace(pair,'')}/{symbol}_{interval}.csv"
        file_exists = os.path.exists(file_path)
        f = open(file_path, "a", newline="")
        writer = csv.writer(f)
        if first_write and not file_exists:
            writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
            first_write = False
        while True:
            print(f"[FETCHING] {symbol} | BATCH: ({batch})")
            data = fetch_symbol_data(symbol=symbol, interval=interval, end_time_ms=end_time)
            if data is None:
                print(f"[+] Finished {symbol} for {interval}")
                break
            for row in reversed(data):
                try:
                    writer.writerow([int(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])])
                except Exception:
                    continue
            end_time = int(data[0][0]) - 1
            batch += 1
            time.sleep(0.2)
        f.close()

def fetch(symbol):
    for i in range(len(intervals)):
        print(f"Fetching: {symbol} | Interval: {intervals[i]}")
        fetch_symbol(symbol=symbol, interval_index=i)
        

if __name__ == "__main__":
    for symbol in symbols:
        fetch(symbol+pair)