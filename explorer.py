import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv("CSP/ETH/ETHUSDT_1m.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['open'] = pd.to_numeric(df['open'], errors='coerce')
df['close'] = pd.to_numeric(df['close'], errors='coerce')

df = df.dropna(subset=['timestamp', 'open', 'close'])

df['price_avg'] = (df['open'] + df['close']) / 2

plt.plot(df['timestamp'], df['price_avg'], marker='', linestyle='-')
close = df['close'].iloc[-1]
closet = df['timestamp'].iloc[-1]
plt.axvline(x=closet, color='red', linestyle='--', linewidth=1)
plt.xlabel("Time")
plt.ylabel("Price AVG")
plt.style.use("dark_background")
plt.grid()
plt.show()