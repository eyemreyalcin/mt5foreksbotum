"""Test Utilities ve Mock Data

Test ve debug amaçlı mock veri oluşturma
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class MockDataGenerator:
    """Mock OHLC veri üretici"""
    
    @staticmethod
    def generate_sample_ohlc(num_candles: int = 500,
                             start_price: float = 1.1000,
                             volatility: float = 0.001) -> pd.DataFrame:
        """
        Örnek OHLC veri üret (test için)
        
        Args:
            num_candles: Candle sayısı
            start_price: Başlangıç fiyatı
            volatility: Oynaklık
            
        Returns:
            OHLC DataFrame
        """
        dates = [datetime.now() - timedelta(hours=i) for i in range(num_candles)][::-1]
        
        prices = [start_price]
        for _ in range(num_candles - 1):
            change = np.random.normal(0, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 0.1))  # Negatif olmasın
        
        data = {
            'Time': dates,
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, volatility))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, volatility))) for p in prices],
            'Close': [p * (1 + np.random.normal(0, volatility)) for p in prices],
            'Volume': np.random.randint(1000, 10000, num_candles),
        }
        
        df = pd.DataFrame(data)
        df.set_index('Time', inplace=True)
        df = df.sort_index()
        
        return df


class MockStrategyResults:
    """Mock strateji sonuçları"""
    
    @staticmethod
    def generate_sample_results(num_strategies: int = 5) -> List[Dict]:
        """
        Örnek strateji sonuçları üret
        
        Args:
            num_strategies: Strateji sayısı
            
        Returns:
            Strateji sonuçları listesi
        """
        indicators = [
            ['RSI_14', 'MACD_12_26_9'],
            ['BB_UPPER', 'ATR_14'],
            ['SMA_50', 'EMA_200'],
            ['RSI_14', 'Stoch_K', 'CCI_20'],
            ['MACD_12_26_9', 'ADOSC'],
        ]
        
        results = []
        for i in range(min(num_strategies, len(indicators))):
            pf = np.random.uniform(1.3, 2.5)
            wr = np.random.uniform(0.55, 0.75)
            dd = np.random.uniform(0.08, 0.20)
            
            result = {
                'strategy_id': f'STR_{i+1:06d}',
                'indicators': indicators[i],
                'timeframe': 'H1',
                'combo_size': len(indicators[i]),
                'total_trades': np.random.randint(50, 300),
                'winning_trades': int(np.random.randint(30, 200)),
                'losing_trades': int(np.random.randint(10, 100)),
                'profit_factor': round(pf, 2),
                'win_rate': round(wr, 4),
                'max_drawdown': round(dd, 4),
                'sharpe_ratio': round(np.random.uniform(0.5, 2.0), 4),
                'sortino_ratio': round(np.random.uniform(0.7, 2.5), 4),
                'total_profit': np.random.randint(500, 5000),
                'total_return': round(np.random.uniform(0.1, 0.5), 4),
                'status': 'pass' if (pf >= 1.5 and wr >= 0.60 and dd <= 0.15) else 'fail',
            }
            results.append(result)
        
        return results


if __name__ == '__main__':
    # Test
    print("Mock OHLC veri örneği:")
    df = MockDataGenerator.generate_sample_ohlc(10)
    print(df)
    
    print("\nMock strateji sonuçları:")
    results = MockStrategyResults.generate_sample_results(3)
    for r in results:
        print(r)
