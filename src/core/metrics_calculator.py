"""Performans Metrikleri Hesaplama Modülü

Bu modül trading strateji performansını değerlendirir:
- Profit Factor (PF)
- Win Rate (WR)
- Maximum Drawdown (DD)
- Sharpe Ratio
- Sortino Ratio
- Recovery Factor
- Vb.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import logging
from scipy import stats

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Trading strateji metrikleri hesaplama"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Args:
            risk_free_rate: Risk-free rate (yıllık, örn 0.02 = %2)
        """
        self.risk_free_rate = risk_free_rate
        
    def calculate_all_metrics(self, trades: List[Dict]) -> Dict:
        """
        Tüm metrikleri bir seferde hesapla
        
        Args:
            trades: Trade listesi [{entry, exit, pnl, ...}, ...]
            
        Returns:
            Metriklerin dict'i
        """
        if not trades:
            logger.warning("Trade listesi boş")
            return {}
        
        pnl_values = np.array([t['pnl'] for t in trades])
        winning_trades = pnl_values[pnl_values > 0]
        losing_trades = pnl_values[pnl_values < 0]
        
        metrics = {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': self.calculate_win_rate(winning_trades, losing_trades),
            'profit_factor': self.calculate_profit_factor(winning_trades, losing_trades),
            'avg_win': np.mean(winning_trades) if len(winning_trades) > 0 else 0,
            'avg_loss': np.mean(losing_trades) if len(losing_trades) > 0 else 0,
            'total_profit': np.sum(pnl_values),
            'largest_win': np.max(winning_trades) if len(winning_trades) > 0 else 0,
            'largest_loss': np.min(losing_trades) if len(losing_trades) > 0 else 0,
        }
        
        return metrics
    
    def calculate_profit_factor(self, winning_trades: np.ndarray,
                               losing_trades: np.ndarray) -> float:
        """
        Profit Factor = Toplam Kazanç / Toplam Zarar
        
        KRİTİK: PF ≥ 1.5 gerekli
        
        Args:
            winning_trades: Kazanan trade'lerin PnL array'i
            losing_trades: Kaybeden trade'lerin PnL array'i
            
        Returns:
            Profit Factor (float)
        """
        total_gains = np.sum(winning_trades) if len(winning_trades) > 0 else 0
        total_losses = np.abs(np.sum(losing_trades)) if len(losing_trades) > 0 else 0
        
        if total_losses == 0:
            return float('inf') if total_gains > 0 else 0
        
        pf = total_gains / total_losses
        return round(pf, 4)
    
    def calculate_win_rate(self, winning_trades: np.ndarray,
                          losing_trades: np.ndarray) -> float:
        """
        Win Rate = Kazanan İşlemler / Toplam İşlemler
        
        KRİTİK: WR ≥ 0.60 (%60) gerekli
        
        Args:
            winning_trades: Kazanan trade'lerin PnL array'i
            losing_trades: Kaybeden trade'lerin PnL array'i
            
        Returns:
            Win Rate (0-1 arasında)
        """
        total_trades = len(winning_trades) + len(losing_trades)
        if total_trades == 0:
            return 0
        
        wr = len(winning_trades) / total_trades
        return round(wr, 4)
    
    def calculate_drawdown(self, equity_curve: np.ndarray) -> Tuple[float, float, int]:
        """
        Maximum Drawdown hesapla
        
        KRİTİK: Max DD ≤ 0.15 (%15) gerekli
        
        Args:
            equity_curve: Bakiye zaman serisi array'i
            
        Returns:
            (max_drawdown_ratio, max_drawdown_value, drawdown_index)
        """
        cumulative_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - cumulative_max) / cumulative_max
        
        max_dd_idx = np.argmin(drawdown)
        max_dd_ratio = abs(drawdown[max_dd_idx])
        max_dd_value = equity_curve[max_dd_idx] - cumulative_max[max_dd_idx]
        
        return round(max_dd_ratio, 4), round(max_dd_value, 2), max_dd_idx
    
    def calculate_sharpe_ratio(self, returns: np.ndarray,
                              periods_per_year: int = 252) -> float:
        """
        Sharpe Ratio = (Avg Return - Risk Free Rate) / Std Dev
        
        Dönem: 1 gün, 252 işlem günü/yıl (forex)
        
        Args:
            returns: Günlük getiri array'i (0-1 arasında)
            periods_per_year: Yılda kaç işlem dönemi (252 = günlük)
            
        Returns:
            Sharpe Ratio (float)
        """
        if len(returns) < 2:
            return 0
        
        # Günlük ortalama getiri
        avg_daily_return = np.mean(returns)
        
        # Günlük getiri volatilitesi
        daily_volatility = np.std(returns)
        
        if daily_volatility == 0:
            return 0
        
        # Yıllık Sharpe Ratio
        excess_return = avg_daily_return - (self.risk_free_rate / periods_per_year)
        sharpe = (excess_return / daily_volatility) * np.sqrt(periods_per_year)
        
        return round(sharpe, 4)
    
    def calculate_sortino_ratio(self, returns: np.ndarray,
                               periods_per_year: int = 252) -> float:
        """
        Sortino Ratio = (Avg Return - Risk Free Rate) / Downside Volatility
        
        Sharpe'den farkı: Sadece aşağı yönlü volatiliteyi dikkate alır
        (yukarı oynaklık göz ardı edilir)
        
        Args:
            returns: Günlük getiri array'i
            periods_per_year: Yılda kaç işlem dönemi
            
        Returns:
            Sortino Ratio (float)
        """
        if len(returns) < 2:
            return 0
        
        # Günlük ortalama getiri
        avg_daily_return = np.mean(returns)
        
        # Sadece negatif günleri al
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return float('inf') if avg_daily_return > 0 else 0
        
        # Downside volatilite
        downside_volatility = np.std(negative_returns)
        
        if downside_volatility == 0:
            return 0
        
        # Yıllık Sortino Ratio
        excess_return = avg_daily_return - (self.risk_free_rate / periods_per_year)
        sortino = (excess_return / downside_volatility) * np.sqrt(periods_per_year)
        
        return round(sortino, 4)
    
    def calculate_calmar_ratio(self, total_return: float,
                              max_drawdown: float) -> float:
        """
        Calmar Ratio = Toplam Return / Max Drawdown
        
        Yüksek değer = daha iyi strateji
        
        Args:
            total_return: Toplam getiri (0-1 arasında)
            max_drawdown: Maximum drawdown (0-1 arasında)
            
        Returns:
            Calmar Ratio (float)
        """
        if max_drawdown == 0:
            return float('inf') if total_return > 0 else 0
        
        calmar = total_return / max_drawdown
        return round(calmar, 4)
    
    def calculate_recovery_factor(self, total_profit: float,
                                 max_drawdown_value: float) -> float:
        """
        Recovery Factor = Toplam Kar ($) / Max Drawdown ($)
        
        Yüksek değer = daha iyih strateji
        
        Args:
            total_profit: Toplam kar ($)
            max_drawdown_value: Max drawdown değeri ($)
            
        Returns:
            Recovery Factor (float)
        """
        if max_drawdown_value == 0 or max_drawdown_value > 0:
            return float('inf') if total_profit > 0 else 0
        
        rf = total_profit / abs(max_drawdown_value)
        return round(rf, 4)
    
    def calculate_consecutive_stats(self, trades: List[Dict]) -> Dict:
        """
        Ardışık kazanç/kayıp istatistikleri
        
        Args:
            trades: Trade listesi
            
        Returns:
            {max_consecutive_wins, max_consecutive_losses, ...}
        """
        if not trades:
            return {}
        
        pnl_values = np.array([t['pnl'] for t in trades])
        
        max_win_streak = 0
        current_win_streak = 0
        max_loss_streak = 0
        current_loss_streak = 0
        
        for pnl in pnl_values:
            if pnl > 0:
                current_win_streak += 1
                max_win_streak = max(max_win_streak, current_win_streak)
                current_loss_streak = 0
            elif pnl < 0:
                current_loss_streak += 1
                max_loss_streak = max(max_loss_streak, current_loss_streak)
                current_win_streak = 0
        
        return {
            'max_consecutive_wins': max_win_streak,
            'max_consecutive_losses': max_loss_streak,
            'current_win_streak': current_win_streak,
            'current_loss_streak': current_loss_streak,
        }
    
    def calculate_expectancy(self, winning_trades: np.ndarray,
                            losing_trades: np.ndarray) -> float:
        """
        Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
        
        Pozitif = trade başına ortalama kâr
        
        Args:
            winning_trades: Kazanan trade'lerin PnL array'i
            losing_trades: Kaybeden trade'lerin PnL array'i
            
        Returns:
            Expectancy (float)
        """
        total_trades = len(winning_trades) + len(losing_trades)
        if total_trades == 0:
            return 0
        
        win_rate = len(winning_trades) / total_trades
        loss_rate = len(losing_trades) / total_trades
        
        avg_win = np.mean(winning_trades) if len(winning_trades) > 0 else 0
        avg_loss = np.mean(losing_trades) if len(losing_trades) > 0 else 0
        
        expectancy = (win_rate * avg_win) - (loss_rate * abs(avg_loss))
        return round(expectancy, 2)
    
    def calculate_payoff_ratio(self, winning_trades: np.ndarray,
                              losing_trades: np.ndarray) -> float:
        """
        Payoff Ratio = Avg Win / Avg Loss
        
        Yüksek değer = daha iyi risk/reward
        
        Args:
            winning_trades: Kazanan trade'lerin PnL array'i
            losing_trades: Kaybeden trade'lerin PnL array'i
            
        Returns:
            Payoff Ratio (float)
        """
        if len(losing_trades) == 0:
            return float('inf') if len(winning_trades) > 0 else 0
        
        avg_win = np.mean(winning_trades) if len(winning_trades) > 0 else 0
        avg_loss = np.abs(np.mean(losing_trades))
        
        if avg_loss == 0:
            return float('inf') if avg_win > 0 else 0
        
        pr = avg_win / avg_loss
        return round(pr, 4)
    
    def filter_by_criteria(self, metrics: Dict,
                          min_pf: float = 1.5,
                          min_wr: float = 0.60,
                          max_dd: float = 0.15) -> Tuple[bool, List[str]]:
        """
        Metriklerin kriterleri sağlayıp sağlamadığını kontrol et
        
        KRİTİK KRITERLER:
        - Profit Factor ≥ 1.5
        - Win Rate ≥ 60%
        - Max Drawdown ≤ 15%
        
        Args:
            metrics: Metrikler dict'i
            min_pf: Minimum Profit Factor
            min_wr: Minimum Win Rate (0-1 arasında)
            max_dd: Maximum Drawdown (0-1 arasında)
            
        Returns:
            (passes_all_criteria, list_of_failures)
        """
        failures = []
        
        # Profit Factor kontrolü
        if metrics.get('profit_factor', 0) < min_pf:
            failures.append(f"PF {metrics.get('profit_factor', 0)} < {min_pf}")
        
        # Win Rate kontrolü
        if metrics.get('win_rate', 0) < min_wr:
            failures.append(f"WR {metrics.get('win_rate', 0):.2%} < {min_wr:.2%}")
        
        # Max Drawdown kontrolü
        # max_drawdown tuple döner: (ratio, value, index)
        dd_ratio = metrics.get('max_drawdown', (0, 0, 0))
        if isinstance(dd_ratio, tuple):
            dd_ratio = dd_ratio[0]
        
        if dd_ratio > max_dd:
            failures.append(f"DD {dd_ratio:.2%} > {max_dd:.2%}")
        
        return len(failures) == 0, failures
    
    def generate_report(self, metrics: Dict,
                       initial_balance: float = 10000) -> str:
        """
        İnsan tarafından okunabilir metrikler raporu üret
        
        Args:
            metrics: Metrikler dict'i
            initial_balance: Başlangıç bakiyesi
            
        Returns:
            Formatlanmış rapor string'i
        """
        report = f"""
╔═══════════════════════════════════════════════════╗
║         STRATEJİ PERFORMANS RAPORU               ║
╠═══════════════════════════════════════════════════╣
║ TRADE METRİKLERİ:                                ║
║   • Toplam Trade: {metrics.get('total_trades', 0)}                        ║
║   • Kazanan: {metrics.get('winning_trades', 0)} ({metrics.get('win_rate', 0):.1%})                   ║
║   • Kaybeden: {metrics.get('losing_trades', 0)}                            ║
║   • Profit Factor: {metrics.get('profit_factor', 0):.2f}x                ║
║                                                   ║
║ PARA METRİKLERİ:                                 ║
║   • Toplam Kar: ${metrics.get('total_profit', 0):,.2f}                   ║
║   • Ort. Kazanç/Trade: ${metrics.get('avg_win', 0):,.2f}                 ║
║   • Ort. Kayıp/Trade: ${metrics.get('avg_loss', 0):,.2f}                 ║
║   • En Büyük Kazanç: ${metrics.get('largest_win', 0):,.2f}               ║
║   • En Büyük Kayıp: ${metrics.get('largest_loss', 0):,.2f}               ║
║                                                   ║
║ RİSK METRİKLERİ:                                 ║
║   • Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}                   ║
║   • Sortino Ratio: {metrics.get('sortino_ratio', 0):.4f}                 ║
║   • Recovery Factor: {metrics.get('recovery_factor', 0):.2f}             ║
║   • Expectancy: ${metrics.get('expectancy', 0):,.2f}                     ║
╚═══════════════════════════════════════════════════╝
"""
        return report
