from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta
from finbert_utils import estimate_sentiment

# ApiKey, ApiSeceret, and baseURL is unique to everyone.
# 1. Make an account on " https://alpaca.markets/ "
# 2. Go to dashboad and go to where it says "API Keys"
# 3. click on "Generate new key"
# 4. Endpoint will be your baseURL 
# 5. Key will be your API Key 
# 6. Secret is your API Secret #


# API_KEY = "PK0F70UN2DTAQ3GDV100"
# API_SECRET = "9Ze3Ll6p65fgZmzoqf3e8bsARzsRAKV9Xpu3tU6n"
# BASE_URL = "https://paper-api.alpaca.markets/v2"

API_KEY = "PKS2U3A28GLKDSB5GZFN"
API_SECRET = "1dUoUIUmTXDSq4gNm7hBnHMWjJDwkZedJifYraX2"
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = { 
    "API_KEY": API_KEY, 
    "API_SECRET": API_SECRET,
    "PAPER": True 
    }


class MLTrader(Strategy):
    def initialize(self, symbol:str = "SPY", cash_at_risk:float = 0.5): #Starts up the bot
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk #
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        pass #Setup 

    def position_sizing(self):
        cash = self.get_cash() 
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity
    
    def get_dates(self):
        today = self.get_datetime()
        threeDaysPrior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), threeDaysPrior.strftime('%Y-%m-%d')
    
    def get_sentiment(self):
        today, threeDaysPrior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start= threeDaysPrior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    

    def on_trading_iteration(self): #runs everytime we get new information
        # Trading Logic 
        
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()
        if cash > last_price:
            if sentiment == "positive" and probability > .999: # checks that we have cash to buy shares 
                if self.last_trade == "sell":
                    self.sell_all()
                print(probability, sentiment)

                order = self.create_order(
                    self.symbol,
                    quantity, 
                    "buy",
                    type="bracket",
                    take_profit_price = last_price*1.20, # sells if hits 20% profit on trade
                    stop_loss_price = last_price*0.95 # sells if loss is -5% on trade
                    )
                self.submit_order(order)
                self.last_trade = "buy"
            elif sentiment == 'negative' and probability > .999:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol, 
                    quantity, 
                    "sell",
                    type="bracket", 
                    take_profit_price= last_price*.8, 
                    stop_loss_price = last_price*1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"

# df.index = df.index.tz_convert('utc')
startDate = datetime(2020, 1, 31) #Y/M/D
endDate = datetime(2023, 12, 31) #Y/M/D

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name = "mlStrat", broker = broker, parameters = {"symbol":"SPY", "cash_at_risk": 0.5})

strategy.backtest(YahooDataBacktesting, startDate, endDate, parameters={"symbol":"SPY", "cash_at_risk": 0.5})
