import os
import urllib.parse
from websocket import create_connection

TOKEN = os.getenv("WS_TOKEN")          # nome da variável
SESSION_ID = os.getenv("WS_SESSION_ID") # nome da variável

if not TOKEN:
    raise SystemExit("WS_TOKEN não definido. Rode: $env:WS_TOKEN='...'")
if not SESSION_ID:
    raise SystemExit("WS_SESSION_ID não definido. Rode: $env:WS_SESSION_ID='...'")

token_q = urllib.parse.quote(str(TOKEN), safe="")
url = f"ws://127.0.0.1:8000/infer/ws/session/{SESSION_ID}?token={token_q}"

print("Connecting:", url[:90] + "...")
ws = create_connection(url)
print("Connected!")
print("Server says:", ws.recv())
ws.close()
print("Closed.")
