from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta


# ApiKey, ApiSeceret, and baseURL is unique to everyone.
# 1. Make an account on " https://alpaca.markets/ "
# 2. Go to dashboad and go to where it says "API Keys"
# 3. click on "Generate new key"
# 4. Endpoint will be your baseURL 
# 5. Key will be your API Key 
# 6. Secret is your API Secret #


API_KEY = "PK0F70UN2DTAQ3GDV100"
API_SECRET = "9Ze3Ll6p65fgZmzoqf3e8bsARzsRAKV9Xpu3tU6n"
BASE_URL = "https://paper-api.alpaca.markets/v2"

AplacaCreds = { "API_KEY": API_KEY, "API_SECRET": API_SECRET, "PAPER": True }

class machineLearningTrader(Strategy):
    def bootUpBot(self, symbol:str = "SPY", cashAtRisk:float = 0.5): #Starts up the bot
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        pass #Setup 

    def position_sizing(self):
        buyingPower = self.get_cash() 
        lastPrice = self.get_last_price(self.symbol)
        quantity = round(buyingPower * self.cashAtRisk / lastPrice, 0)
        return buyingPower, lastPrice, quantity
    
    def get_dates(self):
        today = self.get_datetime()
        threeDaysPrior = today - Timedelta(days=3)
        return today.strfttime("%Y-%m-%d"), threeDaysPrior.strfttime("%Y-%m-%d")
    
    def get_news(self):
        today, threeDaysPrior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start= threeDaysPrior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        return news

    

    def refreshBot(self): #runs everytime we get new information
        # Trading Logic 
        buyingPower, lastPrice, quantity = self.position_sizing()
        if buyingPower > lastPrice: # checks that we have cash to buy shares 
            if self.last_trade == None:
                news = self.get_news()
                order = self.create_order(
                    self.symbol,
                    quantity, 
                    "buy",
                    type="bracket",
                    takeProfit = lastPrice*1.20, # sells if hits 20% profit on trade
                    stopLoss = lastPrice*0.95 # sells if loss is -5% on trade
                    )
                self.submit_order(order)
                self.last_trade = "buy"


startDate = datetime(2024, 5, 15) #Y/M/D
endDate = datetime(2024, 5, 31) #Y/M/D

broker = Alpaca(AplacaCreds)
strategy = machineLearningTrader(name = "mlStrat", broker = broker, parameters = {"symbol":"SPY", "cashAtRisk": 0.5})

strategy.backtest(YahooDataBacktesting, startDate, endDate, parameters={"symbol":"SPY", "cashAtRisk": 0.5})

