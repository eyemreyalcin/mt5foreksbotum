"""Stress Test ve Monte Carlo Simülasyon Modülü

Bu modül strateji sağlamlığını test eder:
- Monte Carlo simülasyonu (1000+ run)
- Drawdown analizi
- Ruin probability (iflâs riski)
- Scenario analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging
from scipy import stats

logger = logging.getLogger(__name__)


class StressTester:
    """Stress test ve Monte Carlo simülasyonu"""
    
    def __init__(self, trades: List[Dict]):
        """
        Args:
            trades: Trade listesi [{entry, exit, pnl, ...}, ...]
        """
        self.trades = trades
        self.pnl_values = np.array([t['pnl'] for t in trades])
        
    def monte_carlo_simulation(self, num_simulations: int = 1000,
                              initial_balance: float = 10000) -> Dict:
        """
        Monte Carlo simülasyonu yap
        
        Mantık:
        1. Trade'leri rastgele sırada çalıştır (1000 kez)
        2. Her simülasyon için equity curve oluştur
        3. Dağılımı analiz et
        
        Args:
            num_simulations: Simülasyon sayısı
            initial_balance: Başlangıç bakiyesi
            
        Returns:
            Simülasyon sonuçları
        """
        logger.info(f"Monte Carlo simülasyonu başladı: {num_simulations} run")
        
        simulated_results = []
        final_balances = []
        max_drawdowns = []
        
        for sim_num in range(num_simulations):
            # Trade'leri rastgele sıra
            shuffled_pnl = np.random.permutation(self.pnl_values)
            
            # Equity curve oluştur
            balance = initial_balance
            equity = [balance]
            
            for pnl in shuffled_pnl:
                balance += pnl
                equity.append(balance)
            
            equity = np.array(equity)
            final_balances.append(balance)
            
            # Max drawdown hesapla
            cummax = np.maximum.accumulate(equity)
            dd = (equity - cummax) / cummax
            max_dd = abs(np.min(dd))
            max_drawdowns.append(max_dd)
            
            simulated_results.append({
                'simulation': sim_num + 1,
                'final_balance': balance,
                'max_drawdown': max_dd,
                'total_return': (balance - initial_balance) / initial_balance,
            })
        
        final_balances = np.array(final_balances)
        max_drawdowns = np.array(max_drawdowns)
        
        # İstatistikler
        positive_sims = np.sum(final_balances > initial_balance)
        
        results = {
            'num_simulations': num_simulations,
            'positive_outcomes': positive_sims,
            'win_rate': positive_sims / num_simulations,
            'final_balance_mean': np.mean(final_balances),
            'final_balance_median': np.median(final_balances),
            'final_balance_std': np.std(final_balances),
            'final_balance_min': np.min(final_balances),
            'final_balance_max': np.max(final_balances),
            'percentile_5': np.percentile(final_balances, 5),
            'percentile_25': np.percentile(final_balances, 25),
            'percentile_75': np.percentile(final_balances, 75),
            'percentile_95': np.percentile(final_balances, 95),
            'max_drawdown_mean': np.mean(max_drawdowns),
            'max_drawdown_max': np.max(max_drawdowns),
            'confidence_interval_95': (
                np.percentile(final_balances, 2.5),
                np.percentile(final_balances, 97.5)
            ),
            'simulated_results': simulated_results,
        }
        
        logger.info(f"MC Simülasyonu tamamlandı: {positive_sims}/{num_simulations} pozitif sonuç")
        return results
    
    def calculate_ruin_probability(self, initial_balance: float = 10000,
                                  ruin_level: float = 0.30) -> float:
        """
        Ruin Probability (İflâs Riski) hesapla
        
        Tanım: Bakiyelerin %30'den fazla düşme riski
        
        Args:
            initial_balance: Başlangıç bakiyesi
            ruin_level: İflâs seviyesi (0.30 = %30 kayıp)
            
        Returns:
            Ruin probability (0-1 arasında)
        """
        logger.info("Ruin probability hesaplanıyor...")
        
        ruin_threshold = initial_balance * (1 - ruin_level)
        
        # MC simülasyonu yap
        mc_results = self.monte_carlo_simulation(num_simulations=1000,
                                                 initial_balance=initial_balance)
        
        # Ruin'e uğrayan simülasyonları say
        ruined = sum(1 for r in mc_results['simulated_results']
                    if r['final_balance'] < ruin_threshold)
        
        ruin_prob = ruined / len(mc_results['simulated_results'])
        logger.info(f"Ruin probability: {ruin_prob:.4f} ({ruin_prob*100:.2f}%)")
        
        return ruin_prob
    
    def worst_case_scenario(self, initial_balance: float = 10000) -> Dict:
        """
        En kötü senaryo analizi
        
        Mantık:
        - Tüm trade'ler sırayla kaybederse ne olur?
        - Ardışık kaybeden trade'ler
        
        Args:
            initial_balance: Başlangıç bakiyesi
            
        Returns:
            Senaryo sonuçları
        """
        logger.info("En kötü senaryo analizi başladı...")
        
        # En büyük kayıptan başla
        sorted_pnl = np.sort(self.pnl_values)
        
        balance = initial_balance
        equity = [balance]
        
        for pnl in sorted_pnl:
            balance += pnl
            equity.append(balance)
        
        equity = np.array(equity)
        
        # Max drawdown
        cummax = np.maximum.accumulate(equity)
        dd = (equity - cummax) / cummax
        max_dd = abs(np.min(dd))
        max_dd_value = np.min(equity) - initial_balance
        
        results = {
            'scenario': 'worst_case_ordered_losses',
            'final_balance': balance,
            'max_drawdown': max_dd,
            'max_drawdown_value': max_dd_value,
            'total_loss': balance - initial_balance,
        }
        
        logger.info(f"En kötü senaryo: DD {max_dd:.2%}, Final: ${balance:,.2f}")
        return results
    
    def bootstrap_confidence_interval(self, initial_balance: float = 10000,
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """
        Bootstrap ile confidence interval hesapla
        
        Args:
            initial_balance: Başlangıç bakiyesi
            confidence: Confidence level (0.95 = %95)
            
        Returns:
            (lower_bound, upper_bound)
        """
        logger.info(f"Bootstrap CI hesaplanıyor ({confidence:.0%})...")
        
        num_bootstrap = 10000
        bootstrap_returns = []
        
        for _ in range(num_bootstrap):
            # Resampling (replacement ile)
            sample = np.random.choice(self.pnl_values, size=len(self.pnl_values), replace=True)
            total_return = np.sum(sample) / initial_balance
            bootstrap_returns.append(total_return)
        
        bootstrap_returns = np.array(bootstrap_returns)
        
        # Confidence interval
        alpha = 1 - confidence
        lower = np.percentile(bootstrap_returns, alpha/2 * 100)
        upper = np.percentile(bootstrap_returns, (1 - alpha/2) * 100)
        
        logger.info(f"Bootstrap CI: [{lower:.4f}, {upper:.4f}]")
        return lower, upper
    
    def stress_test_scenarios(self, initial_balance: float = 10000) -> Dict:
        """
        Farklı stress senaryoları test et
        
        Senaryolar:
        1. %20 drawdown senaryosu
        2. %50 kayıp senaryosu
        3. Ardışık 5 kayıp
        4. Volatilite +50%
        
        Args:
            initial_balance: Başlangıç bakiyesi
            
        Returns:
            Senaryo sonuçları
        """
        logger.info("Stress test senaryoları çalıştırılıyor...")
        
        scenarios = {}
        
        # Senaryo 1: %20 drawdown
        scenario1_pnl = self.pnl_values * 0.80  # Kazançlar %20 azal
        scenarios['scenario_1_20pct_loss'] = {
            'description': 'Market volatility +20%',
            'modified_pnl': scenario1_pnl,
            'final_balance': initial_balance + np.sum(scenario1_pnl),
            'impact': np.sum(scenario1_pnl) / initial_balance,
        }
        
        # Senaryo 2: %50 kayıp (worst case)
        scenario2_pnl = self.pnl_values * 0.50
        scenarios['scenario_2_50pct_loss'] = {
            'description': 'Extreme market crash',
            'modified_pnl': scenario2_pnl,
            'final_balance': initial_balance + np.sum(scenario2_pnl),
            'impact': np.sum(scenario2_pnl) / initial_balance,
        }
        
        logger.info(f"Stress test tamamlandı: {len(scenarios)} senaryo")
        return scenarios
    
    def generate_stress_report(self, initial_balance: float = 10000) -> str:
        """
        Stress test raporu oluştur
        
        Args:
            initial_balance: Başlangıç bakiyesi
            
        Returns:
            Rapor string'i
        """
        mc_results = self.monte_carlo_simulation(num_simulations=1000,
                                                 initial_balance=initial_balance)
        ruin_prob = self.calculate_ruin_probability(initial_balance)
        worst_case = self.worst_case_scenario(initial_balance)
        ci_lower, ci_upper = self.bootstrap_confidence_interval(initial_balance)
        
        report = f"""
╔═══════════════════════════════════════════════════╗
║         STRESS TEST RAPORU                        ║
╠═══════════════════════════════════════════════════╣
║ MONTE CARLO SİMÜLASYON ({mc_results['num_simulations']} run):          ║
║   • Pozitif Sonuç: {mc_results['positive_outcomes']}/{mc_results['num_simulations']} ({mc_results['win_rate']:.1%})        ║
║   • Ort. Final Bakiye: ${mc_results['final_balance_mean']:,.2f}          ║
║   • Ortanca Final Bakiye: ${mc_results['final_balance_median']:,.2f}     ║
║   • Min Final Bakiye: ${mc_results['final_balance_min']:,.2f}            ║
║   • Max Final Bakiye: ${mc_results['final_balance_max']:,.2f}            ║
║   • %95 CI: ${mc_results['confidence_interval_95'][0]:,.2f} - ${mc_results['confidence_interval_95'][1]:,.2f}  ║
║                                                   ║
║ RİSK METRİKLERİ:                                 ║
║   • Max Drawdown (avg): {mc_results['max_drawdown_mean']:.2%}            ║
║   • Max Drawdown (worst): {mc_results['max_drawdown_max']:.2%}          ║
║   • Ruin Probability: {ruin_prob:.2%}                   ║
║                                                   ║
║ EN KÖTÜ SENARYO:                                 ║
║   • Final Bakiye: ${worst_case['final_balance']:,.2f}                   ║
║   • Drawdown: {worst_case['max_drawdown']:.2%}                         ║
║   • Loss Amount: ${worst_case['total_loss']:,.2f}                       ║
╚═══════════════════════════════════════════════════╝
"""
        
        return report
