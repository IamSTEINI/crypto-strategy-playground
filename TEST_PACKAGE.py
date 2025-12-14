import datetime
import time
import strategy_backtesting as sb
import pandas as pd


# Settings for simulation
settings = sb.Settings(timespan=1000, buy_amount=1, sell_amount=1)

# Creating the chart object
eth_chart = sb.ChartManager()

# Applying the settings to the chart object, eg. default money or timespan of simulation
eth_chart.set_chart_settings(settings=settings)

# SETTING THE CHART DATA YOU WANT TO BACKTEST
# MUST BE IN THE FOLLOWING CSV FORMAT:
# timestamp,open,high,low,close,volume
# YOU CAN USE THE 'fetch_symbol_charts.py' file to retrieve much csv files (crypto)
eth_chart.set_chart_data(pd.read_csv("ETHUSDT_1h.csv").iloc[::-1])

# Getting the data to build our simulation on
experiment_chart = eth_chart.get_chart_data()

# Let's say we always want to buy when the RSI is below 20
# The RSI, EMA (25,50,100,150,200,400) and the MACD (Line, Signal, Histogram line) 
# are supported within the rows ["RSI", "EMA25", "EMA...", "MACD_SIGN", "MACD_HIST", "MACD"]

# Lets add arrays for the simulation to know when to buy and some settings
buy_data = []
sell_data = []
oversold = 30
overbought = 70

# Adding buy and sell data
# === IN THIS PART YOU CAN MAKE YOUR OWN STRATEGIES with ['open', 'high', 'low', 'close', 'volume'] and more!
for _, row in experiment_chart.iterrows():
    if not pd.notna(row["RSI"]):
        continue
    rsi = row["RSI"]
    # Checking the RSI
    if rsi < oversold:
        buy_data.append([row["timestamp"], row.get("close")]) # BUYING when the RSI is below our setting
    elif rsi > overbought:
        sell_data.append([row["timestamp"], row.get("close")]) # SELLING when the RSI is above our setting


# Applying this data to our strategy
strategy = sb.Strategy(name="RSI Strategy")
strategy.set_strategy_buys(buys=buy_data)
strategy.set_strategy_sells(sells=sell_data)

# FINISH! Let's simulate our strategy

simulation = sb.Simulation(chart=experiment_chart, settings=settings, strategy=strategy)
portfolio = simulation.simulate()

# Let's print our final BALANCE
print("TOTAL PnL: "+str(round((portfolio["balance"].iloc[-1])-settings.default_money, 2))+"$")

# GET A GRAPH FROM PORTFOLIO OVER TIME
# You can also add EMA Lines or RSI
#simulation.graph(rsi=True, rsi_over=[oversold, overbought], ema=True)

# Now lets apply our strategy to the live data
# And our strategy function

df = pd.DataFrame()
simulated_assets = 0
simulated_money = 10000

def calcRSI(avg_gain, avg_loss):
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def strategyFunction(data):
    global df, simulated_assets, simulated_money
    # Here we receive price data and while its running we get the indicators so we add every entry to our strategy list
    append = {
        "timestamp": data['T'],
        "close": float(data['p']),
        "signal": None
    }
    
    new = pd.DataFrame([append])
    df = pd.concat([df, new], ignore_index=True)
    
    # ADDING THE RSI STRATEGY HERE
    if len(df) >= 100:
        df_temp = df.copy()
        df_temp['change'] = df_temp['close'].diff()
        df_temp['gain'] = df_temp['change'].clip(lower=0)
        df_temp['loss'] = -df_temp['change'].clip(upper=0)
        df_temp['avggain'] = df_temp['gain'].rolling(14).mean()
        df_temp['avgloss'] = df_temp['loss'].rolling(14).mean()
        
        current_rsi = calcRSI(
            df_temp['avggain'].iloc[-1], 
            df_temp['avgloss'].iloc[-1]
        )
        
        if current_rsi < 10:
            df.loc[df.index[-1], 'signal'] = 'buy'
            simulated_assets += 0.01
            simulated_money -= 0.01 * float(data['p'])
            print(f"[BUY] SIGNAL ${data['p']} (RSI: {current_rsi:.2f})")
        
        elif current_rsi > 90:
            df.loc[df.index[-1], 'signal'] = 'sell'
            if simulated_assets >= 0.01:
                simulated_assets -= 0.01
                simulated_money += 0.01 *float(data['p'])
            print(f"[SELL] SIGNAL ${data['p']} (RSI: {current_rsi:.2f})")
            
        # BUYING / SELLING IF RSI IS ABOVE OR BELOW

        print(f"{simulated_money}$\t{simulated_assets}ETH\t{simulated_assets*float(data['p'])}$ Unrealized\t\tPROFIT: {(simulated_money + (simulated_assets*float(data['p']))) - 10000}$")


# TODO Combined data points (1m,15min, etc...)

url = 'wss://stream.binance.com:9443/ws/'
symbol = 'ethusdt'
stream = '@aggTrade'
long_url = url+symbol+stream
session = sb.Session(websocketURL=long_url, strategy=strategyFunction)
session.start()

#Giving it time to connect
time.sleep(3)

session.live_chart(
    df_getter=lambda: df, # DATAFRAME
    interval=0, # UPDATE INTERVAL
    max_p=10000, # MAX. DATA POINTS
    show_ema=True, # EMA LINES
    show_rsi=True, # RSI
    rsi_levels=[30, 70] # RSI, 30 LOW, 70 UP
)

while(session.running):
    time.sleep(1)
