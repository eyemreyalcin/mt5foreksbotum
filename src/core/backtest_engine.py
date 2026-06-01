"""Backtest Motor Modülü

Bu modül geçmiş veriler üzerinde strateji backtesting yapar.
Backtest ve Walk Forward test'ini destekler.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtest motoru - strateji test etme"""
    
    def __init__(self, df: pd.DataFrame, initial_balance: float = 10000):
        """
        Args:
            df: OHLC DataFrame (index = datetime, columns = Open, High, Low, Close, Volume)
            initial_balance: Başlangıç bakiyesi ($)
        """
        self.df = df.copy()
        self.initial_balance = initial_balance
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(self, indicators_signals: pd.DataFrame,
                    buy_signal_col: str,
                    sell_signal_col: str,
                    position_size: float = 0.1,
                    stop_loss_pips: float = 50,
                    take_profit_pips: float = 150) -> Dict:
        """
        Basit backtest çalıştır
        
        Args:
            indicators_signals: İndikatör sinyalleri (DataFrame)
            buy_signal_col: Alış sinyali sütun adı (True/False)
            sell_signal_col: Satış sinyali sütun adı (True/False)
            position_size: Pozisyon boyutu (lot)
            stop_loss_pips: Stop loss (pips)
            take_profit_pips: Take profit (pips)
            
        Returns:
            Backtest sonuçları dict'i
        """
        logger.info("Backtest başladı...")
        
        balance = self.initial_balance
        position = None  # None = pozisyon yok, 'long' veya 'short'
        entry_price = None
        entry_time = None
        
        for idx in range(len(self.df)):
            timestamp = self.df.index[idx]
            close = self.df['Close'].iloc[idx]
            high = self.df['High'].iloc[idx]
            low = self.df['Low'].iloc[idx]
            
            # Al sinyali
            if indicators_signals[buy_signal_col].iloc[idx] and position is None:
                position = 'long'
                entry_price = close
                entry_time = timestamp
                logger.debug(f"AL sinyali: {timestamp}, Fiyat: {close}")
            
            # Sat sinyali veya stop loss / take profit kontrol
            elif position == 'long':
                # Stop loss kontrol
                if low <= entry_price - (stop_loss_pips * 0.0001):
                    pnl = (entry_price - (entry_price - (stop_loss_pips * 0.0001))) * position_size * 100000
                    balance += pnl
                    self.trades.append({
                        'entry_time': entry_time,
                        'exit_time': timestamp,
                        'entry_price': entry_price,
                        'exit_price': entry_price - (stop_loss_pips * 0.0001),
                        'pnl': pnl,
                        'reason': 'stop_loss',
                    })
                    position = None
                    logger.debug(f"STOP LOSS: PnL: {pnl}")
                
                # Take profit kontrol
                elif high >= entry_price + (take_profit_pips * 0.0001):
                    pnl = (take_profit_pips * 0.0001) * position_size * 100000
                    balance += pnl
                    self.trades.append({
                        'entry_time': entry_time,
                        'exit_time': timestamp,
                        'entry_price': entry_price,
                        'exit_price': entry_price + (take_profit_pips * 0.0001),
                        'pnl': pnl,
                        'reason': 'take_profit',
                    })
                    position = None
                    logger.debug(f"TAKE PROFIT: PnL: {pnl}")
                
                # Sat sinyali
                elif indicators_signals[sell_signal_col].iloc[idx]:
                    pnl = (close - entry_price) * position_size * 100000
                    balance += pnl
                    self.trades.append({
                        'entry_time': entry_time,
                        'exit_time': timestamp,
                        'entry_price': entry_price,
                        'exit_price': close,
                        'pnl': pnl,
                        'reason': 'sell_signal',
                    })
                    position = None
                    logger.debug(f"SAT sinyali: PnL: {pnl}")
            
            # Bakiyeyi kaydet
            self.equity_curve.append(balance)
        
        # Açık pozisyon kapatılırsa
        if position == 'long':
            pnl = (self.df['Close'].iloc[-1] - entry_price) * position_size * 100000
            balance += pnl
            self.trades.append({
                'entry_time': entry_time,
                'exit_time': self.df.index[-1],
                'entry_price': entry_price,
                'exit_price': self.df['Close'].iloc[-1],
                'pnl': pnl,
                'reason': 'end_of_data',
            })
        
        logger.info(f"Backtest tamamlandı: {len(self.trades)} trade")
        
        return self._calculate_backtest_results()
    
    def _calculate_backtest_results(self) -> Dict:
        """
        Backtest sonuçlarını hesapla
        
        Returns:
            Sonuçlar dict'i
        """
        if not self.trades:
            return {'error': 'No trades executed'}
        
        equity_array = np.array(self.equity_curve)
        pnl_array = np.array([t['pnl'] for t in self.trades])
        
        total_return = (equity_array[-1] - self.initial_balance) / self.initial_balance
        winning_trades = pnl_array[pnl_array > 0]
        losing_trades = pnl_array[pnl_array < 0]
        
        results = {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.trades) if len(self.trades) > 0 else 0,
            'total_return': total_return,
            'total_profit': equity_array[-1] - self.initial_balance,
            'equity_curve': equity_array,
        }
        
        return results
    
    def run_walk_forward_test(self, 
                             indicators_df: pd.DataFrame,
                             buy_signal_col: str,
                             sell_signal_col: str,
                             train_days: int = 365,
                             test_days: int = 90,
                             step_days: int = 30) -> List[Dict]:
        """
        İleri dönük test (Walk Forward Test)
        
        Mantık:
        1. Eğitim verisi üzerinde optimize et
        2. Test verisi üzerinde test et
        3. Pencereyi ilerlet ve tekrarla
        
        Args:
            indicators_df: İndikatör DataFrame'i
            buy_signal_col: Alış sinyali
            sell_signal_col: Satış sinyali
            train_days: Eğitim penceresi (gün)
            test_days: Test penceresi (gün)
            step_days: Pencere kaydırma (gün)
            
        Returns:
            Her walk'ın sonuçları listesi
        """
        logger.info("Walk Forward Test başladı...")
        
        results = []
        walk_num = 1
        
        # Tarih temeline göre pencereler oluştur
        total_days = len(self.df)
        
        for start_idx in range(0, total_days - train_days - test_days, step_days):
            train_end_idx = start_idx + train_days
            test_end_idx = train_end_idx + test_days
            
            if test_end_idx > total_days:
                break
            
            # Eğitim ve test verisi
            train_data = self.df.iloc[start_idx:train_end_idx]
            test_data = self.df.iloc[train_end_idx:test_end_idx]
            
            train_signals = indicators_df.iloc[start_idx:train_end_idx]
            test_signals = indicators_df.iloc[train_end_idx:test_end_idx]
            
            logger.info(f"Walk {walk_num}: Train {train_data.index[0]} - {train_data.index[-1]}, "
                       f"Test {test_data.index[0]} - {test_data.index[-1]}")
            
            # Test et
            test_engine = BacktestEngine(test_data, self.initial_balance)
            test_results = test_engine.run_backtest(
                test_signals,
                buy_signal_col,
                sell_signal_col
            )
            
            test_results['walk_num'] = walk_num
            test_results['train_start'] = train_data.index[0]
            test_results['train_end'] = train_data.index[-1]
            test_results['test_start'] = test_data.index[0]
            test_results['test_end'] = test_data.index[-1]
            
            results.append(test_results)
            walk_num += 1
        
        logger.info(f"Walk Forward Test tamamlandı: {len(results)} walk")
        return results
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """
        Trade'leri DataFrame'e dönüştür
        
        Returns:
            Trade DataFrame'i
        """
        if not self.trades:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.trades)
        df['profit_loss_pct'] = (df['pnl'] / self.initial_balance) * 100
        
        return df
