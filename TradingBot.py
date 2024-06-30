from lumibot.brokers import Aplaca
from lumibot.backtesting import YahooDataBackTesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import trader
from datetime import datetime


# ApiKey, ApiSeceret, and baseURL is unique to everyone.
# 1. Make an account on " https://alpaca.markets/ "
# 2. Go to dashboad and go to where it says "API Keys"
# 3. click on "Generate new key"
# 4. Endpoint will be your baseURL 
# 5. Key will be your API Key 
# 6. Secret is your API Secret #
ApiKey = "PK0F70UN2DTAQ3GDV100"
ApiSecret = "9Ze3Ll6p65fgZmzoqf3e8bsARzsRAKV9Xpu3tU6n"
BaseURL = "https://paper-api.alpaca.markets/v2"

AplacaCreds = { "API_ KEY": ApiKey, "API_SECRET": ApiSecret, "PAPER": True }

broker = Alpaca(AplacaCreds)
