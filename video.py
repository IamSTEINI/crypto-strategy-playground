import pandas as pd

import strategy_backtesting

settings = strategy_backtesting.Settings(timespan=1000, buy_amount=1, sell_amount=1)

eth_chart = strategy_backtesting.ChartManager()
eth_chart.set_chart_settings(settings=settings)
eth_chart.set_chart_data(pd.read_csv("ETHUSDT_1h.csv").iloc[::-1])

experiment_chart = eth_chart.get_chart_data()

buys = []
sells = []
oversold = 30
overbought = 70

for _, row in experiment_chart.iterrows():
    if not pd.notna(row["RSI"]):
        continue

    rsi = row["RSI"]
    if rsi < oversold:
        buys.append([row["timestamp"], row.get("close")])
    elif rsi > overbought:
        sells.append([row["timestamp"], row.get("close")])


strategy = strategy_backtesting.Strategy(name="MY RSI STRATEGY")
strategy.set_strategy_buys(buys=buys)
strategy.set_strategy_sells(sells=sells)

simulation = strategy_backtesting.Simulation(chart=experiment_chart, settings=settings, strategy=strategy)
portfolio = simulation.simulate()

print("REALIZED PnL: "+str(round(portfolio["balance"].iloc[-1]-settings.default_money, 2)))