import yfinance as yf
import pandas as pd
import time

class FinProvider:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # Seconds

    def get_data(self, symbol):
        """
        Market se live data fetch karne ke liye upgraded logic.
        Ab isme retries aur data cleaning bhi shamil hai.
        """
        for attempt in range(self.max_retries):
            try:
                # 1-minute interval data fetch kar rahe hain
                data = yf.download(
                    tickers=symbol,
                    period="1d",
                    interval="1m",
                    progress=False,
                    auto_adjust=True
                )
                
                if data is not None and not data.empty:
                    # Data Cleaning: Null values hatana
                    data = data.dropna()
                    
                    # Basic Technical Indicators yahan hi add kar dete hain taake engine fast chale
                    if len(data) > 20:
                        data['SMA_20'] = data['Close'].rolling(window=20).mean()
                        data['EMA_10'] = data['Close'].ewm(span=10, adjust=False).mean()
                    
                    return data
                
                print(f"Attempt {attempt + 1}: No data found for {symbol}. Retrying...")
                
            except Exception as e:
                print(f"Attempt {attempt + 1} Error: {e}")
            
            # Wait before retrying
            time.sleep(self.retry_delay)
            
        return None

    def get_asset_info(self, symbol):
        """
        Asset ki mazeed details (Currency, Exchange) nikalne ke liye.
        """
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except:
            return {}
