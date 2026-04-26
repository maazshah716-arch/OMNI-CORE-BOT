import yfinance as yf
import pandas as pd

class FinProvider:
    def __init__(self):
        pass

    def get_data(self, symbol):
        """
        Market se live data fetch karne ke liye.
        """
        try:
            # 1-minute interval data for live trading feel
            data = yf.download(
                tickers=symbol,
                period="1d",
                interval="1m",
                progress=False
            )
            
            if data.empty:
                return None
                
            return data
        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return None
