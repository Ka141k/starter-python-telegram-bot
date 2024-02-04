import os

TOKEN = os.environ['TOKEN']

OWNER_ID = 5217286050


WEBHOOK_PATH = "/webhook"
SERVER_URL = "https://YOUR-NGROK-URL.ngrok-free.app"
WEBHOOK_URL = f"{SERVER_URL}{WEBHOOK_PATH}"

HOST, PORT = "127.0.0.1", 8080