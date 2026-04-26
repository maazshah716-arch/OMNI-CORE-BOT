import yfinance as yf 
import pandas as pd 
class FinProvider: 
    def get_data(self, s): 
        try: 
            d = yf.download(s, period='1d', interval='1m', progress=False) 
            if not d.empty: 
                df = d.copy() 
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0) 
                return df 
            return None 
        except: return None 
