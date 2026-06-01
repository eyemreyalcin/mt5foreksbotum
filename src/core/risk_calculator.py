"""Risk Management and Position Sizing Calculator

Bu modül akıllı risk yönetimi sağlar:
- Per-trade %2 risk ile position sizing
- Bakiye güncellemesi
- Risk metrikleri hesaplama
"""

import numpy as np
from typing import Dict, Tuple


class RiskCalculator:
    """Pozisyon büyüklüğü ve risk yönetimi"""
    
    def __init__(self, initial_balance: float = 10000, 
                 max_risk_per_trade: float = 0.02):
        """
        Args:
            initial_balance: Başlangıç bakiyesi ($)
            max_risk_per_trade: Per-trade maksimum risk oranı (0.02 = %2)
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.max_risk_per_trade = max_risk_per_trade
        self.trade_history = []
        
    def calculate_position_size(self, entry_price: float, 
                                stop_loss_price: float,
                                pip_value: float = 0.0001) -> float:
        """
        Giriş fiyatı ve stop loss'a göre lot boyutunu hesapla
        
        Args:
            entry_price: Giriş fiyatı
            stop_loss_price: Stop loss fiyatı
            pip_value: 1 pip'in değeri (forex için 0.0001, altın için 0.01)
            
        Returns:
            Lot boyutu (0.01 minimu)
            
        Örnek:
            >>> risk_calc = RiskCalculator(initial_balance=10000)
            >>> position_size = risk_calc.calculate_position_size(
            ...     entry_price=1.1000, 
            ...     stop_loss_price=1.0950
            ... )
            >>> print(f"Position size: {position_size} lot")
        """
        # Risk tutarı = bakiye × %2
        risk_amount = self.current_balance * self.max_risk_per_trade
        
        # Fiyat farkı (pips)
        price_diff = abs(entry_price - stop_loss_price)
        
        # 1 pip başına risk
        pips_risk = price_diff / pip_value
        
        if pips_risk == 0:
            return 0.01  # Minimum lot
        
        # Position size = Risk tutarı / (pips × pip değeri)
        # 1 lot = 100,000 unit (standart forex)
        position_size = risk_amount / (pips_risk * pip_value * 100000)
        
        # Minimum 0.01 lot
        position_size = max(position_size, 0.01)
        
        return round(position_size, 2)
    
    def calculate_take_profit(self, entry_price: float, 
                             stop_loss_price: float,
                             reward_risk_ratio: float = 2.0) -> float:
        """
        Risk/Reward oranına göre take profit hesapla
        
        Args:
            entry_price: Giriş fiyatı
            stop_loss_price: Stop loss fiyatı
            reward_risk_ratio: Risk/Reward oranı (2:1 = 2.0)
            
        Returns:
            Take profit fiyatı
        """
        risk_distance = abs(entry_price - stop_loss_price)
        reward_distance = risk_distance * reward_risk_ratio
        
        if entry_price > stop_loss_price:  # Long pozisyon
            take_profit = entry_price + reward_distance
        else:  # Short pozisyon
            take_profit = entry_price - reward_distance
            
        return round(take_profit, 5)
    
    def update_balance(self, pnl: float, trade_details: Dict = None) -> float:
        """
        Trade sonrası bakiyeyi güncelle
        
        Args:
            pnl: Kar/Zarar ($)
            trade_details: Trade detayları (isteğe bağlı)
            
        Returns:
            Yeni bakiye
        """
        self.current_balance += pnl
        
        # Trade history'ye ekle
        if trade_details is None:
            trade_details = {}
        trade_details['pnl'] = pnl
        trade_details['balance_after'] = self.current_balance
        self.trade_history.append(trade_details)
        
        return self.current_balance
    
    def calculate_drawdown(self, equity_curve: np.ndarray) -> Tuple[float, float, int]:
        """
        Equity curve'den drawdown hesapla
        
        Args:
            equity_curve: Bakiye zaman serisi
            
        Returns:
            (max_drawdown_ratio, max_drawdown_amount, max_dd_index)
        """
        cumulative_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - cumulative_max) / cumulative_max
        
        max_drawdown_idx = np.argmin(drawdown)
        max_drawdown = drawdown[max_drawdown_idx]
        max_drawdown_amount = equity_curve[max_drawdown_idx] - cumulative_max[max_drawdown_idx]
        
        return abs(max_drawdown), abs(max_drawdown_amount), max_drawdown_idx
    
    def calculate_recovery_factor(self, total_profit: float, 
                                  max_drawdown_amount: float) -> float:
        """
        Recovery Factor = Total Profit / Max Drawdown
        Yüksek değer = daha iyi strateji
        
        Args:
            total_profit: Toplam kar ($)
            max_drawdown_amount: Maximum Drawdown tutarı ($)
            
        Returns:
            Recovery Factor
        """
        if max_drawdown_amount == 0:
            return float('inf') if total_profit > 0 else 0
        
        return total_profit / max_drawdown_amount
    
    def calculate_profit_factor(self, winning_trades: np.ndarray, 
                               losing_trades: np.ndarray) -> float:
        """
        Profit Factor = Toplam Kazanç / Toplam Zarar
        Kritik: PF ≥ 1.5 gerekli
        
        Args:
            winning_trades: Kazanan trade PnL'leri
            losing_trades: Kaybeden trade PnL'leri
            
        Returns:
            Profit Factor
        """
        total_gains = np.sum(winning_trades)
        total_losses = np.abs(np.sum(losing_trades))
        
        if total_losses == 0:
            return float('inf') if total_gains > 0 else 0
        
        return total_gains / total_losses
    
    def calculate_win_rate(self, winning_trades: np.ndarray, 
                          losing_trades: np.ndarray) -> float:
        """
        Win Rate = Kazanan İşlemler / Toplam İşlemler
        Kritik: WR ≥ 60% gerekli
        
        Args:
            winning_trades: Kazanan trade PnL'leri
            losing_trades: Kaybeden trade PnL'leri
            
        Returns:
            Win Rate (0-1 arası)
        """
        total_trades = len(winning_trades) + len(losing_trades)
        if total_trades == 0:
            return 0
        
        return len(winning_trades) / total_trades
    
    def reset(self):
        """Bakiyeyi ve trade history'yi sıfırla"""
        self.current_balance = self.initial_balance
        self.trade_history = []
