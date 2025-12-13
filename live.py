import websocket
import json

def on_message(_ws, message):
    data = json.loads(message)
    print(data)

def on_error(_ws, error):
    print(f"Error: {error}")
    
def on_close(_ws, _close_status_code, _close_msg):
    print("Closed")
    
url = 'wss://stream.binance.com:9443/ws/'
symbol = 'ethusdt'
stream = '@aggTrade'
long_url = url+symbol+stream
ws = websocket.WebSocketApp(long_url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.run_forever()