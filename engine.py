import pandas as pd
import numpy as np

class TradeEngine:
    def __init__(self):
        self.stability_count = 0
        self.required_stability = 2  # Signal stability check (ticks)
        self.last_signal = "WAITING"

    def calculate_indicators(self, df):
        # 1. RSI Calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # 2. Bollinger Bands (Volatility Filter)
        df['sma'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['sma'] + (2 * df['std'])
        df['lower_band'] = df['sma'] - (2 * df['std'])
        
        return df

    def generate_signal(self, df):
        if len(df) < 20:
            return "WAITING", 0
            
        df = self.calculate_indicators(df)
        last_row = df.iloc[-1]
        
        current_price = last_row['close']
        rsi = last_row['rsi']
        upper_b = last_row['upper_band']
        lower_b = last_row['lower_band']

        # Institutional Confluence Logic
        # Condition: Price must touch Band AND RSI must be Overbought/Oversold
        potential_signal = "WAITING"
        
        if rsi < 30 and current_price <= lower_b:
            potential_signal = "CALL"
        elif rsi > 70 and current_price >= upper_b:
            potential_signal = "PUT"

        # Signal Stability Counter (Anti-Fake Signal)
        if potential_signal == self.last_signal and potential_signal != "WAITING":
            self.stability_count += 1
        else:
            self.stability_count = 0
            self.last_signal = potential_signal

        # Accuracy Score (Confidence)
        confidence = 0
        if potential_signal != "WAITING":
            # Confidence increases with RSI extreme levels
            confidence = 85 + (abs(50 - rsi) / 5) 
            
        # Final Confirmation after stability check
        if self.stability_count >= self.required_stability:
            return potential_signal, round(min(confidence, 99), 2)
        
        return "WAITING", 0