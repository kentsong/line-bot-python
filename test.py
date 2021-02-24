import yfinance as yf
print("1111")


asset_symbol = "2330.TW"

stock = yf.Ticker(asset_symbol)
# get historical market data
data = stock.history(period="max")

stock.actions