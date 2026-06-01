"""Strateji Kombinasyon Üretim Modülü

Bu modül otomatik olarak indikatör kombinasyonları üretir:
- 2'li, 3'lü, 4'lü kombinasyonlar
- Korelasyon filtreleme (yüksek korele olanları ayırır)
- Akıllı sampling (çok fazla kombinasyon oluşmasını önler)
"""

import numpy as np
import pandas as pd
from itertools import combinations
from typing import List, Dict, Tuple, Set
import logging
from sklearn.cluster import AgglomerativeClustering

logger = logging.getLogger(__name__)


class StrategyGenerator:
    """Strateji kombinasyon üretimi"""
    
    def __init__(self, correlation_matrix: pd.DataFrame,
                 correlation_limit: float = 0.70):
        """
        Args:
            correlation_matrix: İndikatörler arası korelasyon matrisi
            correlation_limit: Korelasyon limiti (0.7 = %70'den fazla korele olanları ayır)
        """
        self.correlation_matrix = correlation_matrix
        self.correlation_limit = correlation_limit
        self.strategies = []
        
    def filter_correlated_indicators(self) -> List[str]:
        """
        Yüksek korele indikatörleri filtrele
        
        Mantık: Eğer iki indikatör %70'den fazla korele ise,
        birini kaldır (daha az işe yarar olan)
        
        Returns:
            Kullanılacak indikatörlerin listesi
        """
        logger.info("Korele indikatörler filtreleniyor...")
        
        # İndikatör adlarını al
        indicators = self.correlation_matrix.columns.tolist()
        to_remove = set()
        
        # Korelasyon matrisini kontrol et
        for i, ind1 in enumerate(indicators):
            if ind1 in to_remove:
                continue
            
            for j, ind2 in enumerate(indicators[i+1:], start=i+1):
                if ind2 in to_remove:
                    continue
                
                # Korelasyon değeri
                corr = abs(self.correlation_matrix.loc[ind1, ind2])
                
                # Eğer çok yüksek koreleli ise
                if corr > self.correlation_limit:
                    # Daha az değişken olan (daha düz olan) kaldır
                    var1 = self.correlation_matrix[ind1].var()
                    var2 = self.correlation_matrix[ind2].var()
                    
                    if var1 < var2:
                        to_remove.add(ind1)
                    else:
                        to_remove.add(ind2)
        
        filtered = [ind for ind in indicators if ind not in to_remove]
        logger.info(f"Filtreleme sonucu: {len(indicators)} -> {len(filtered)} indikatör")
        
        return filtered
    
    def generate_combinations(self, indicators: List[str],
                             combo_types: List[int] = [2, 3, 4]) -> List[Tuple]:
        """
        İndikatör kombinasyonları oluştur
        
        Args:
            indicators: İndikatör listesi
            combo_types: Kombinasyon türleri [2, 3, 4]
            
        Returns:
            Kombinasyon tuple'larının listesi
            
        Örnek:
            >>> indicators = ['RSI_14', 'MACD_12_26_9', 'BB_UPPER']
            >>> combos = gen.generate_combinations(indicators, [2])
            >>> print(combos)
            [('RSI_14', 'MACD_12_26_9'), ('RSI_14', 'BB_UPPER'), ...]
        """
        logger.info(f"Kombinasyonlar oluşturuluyor: {combo_types}")
        
        all_combos = []
        total_possible = 0
        
        for combo_type in combo_types:
            if combo_type <= len(indicators):
                combos = list(combinations(indicators, combo_type))
                all_combos.extend(combos)
                total_possible += len(combos)
                logger.info(f"  {combo_type}'li: {len(combos)} kombinasyon")
        
        logger.info(f"Toplam kombinasyon: {len(all_combos)}")
        
        return all_combos
    
    def generate_strategies(self, combinations_list: List[Tuple],
                           timeframes: List[int] = [1, 4]) -> List[Dict]:
        """
        Kombinasyonlardan strateji tanımı oluştur
        
        Args:
            combinations_list: İndikatör kombinasyonları
            timeframes: Zaman dilimleri [1, 4] = [H1, H4]
            
        Returns:
            Strateji tanımlarının listesi
        """
        logger.info(f"Stratejiler oluşturuluyor: {len(combinations_list)} × {len(timeframes)} TF...")
        
        strategies = []
        strategy_id = 1
        
        for combo in combinations_list:
            for tf in timeframes:
                strategy = {
                    'id': f'STR_{strategy_id:06d}',
                    'indicators': combo,
                    'timeframe': tf,
                    'combo_size': len(combo),
                    'status': 'pending',
                }
                strategies.append(strategy)
                strategy_id += 1
        
        logger.info(f"Toplam strateji oluşturuldu: {len(strategies)}")
        self.strategies = strategies
        
        return strategies
    
    def smart_sample_strategies(self, strategies: List[Dict],
                               max_strategies: int = 1000) -> List[Dict]:
        """
        Çok fazla strateji oluştuğunda akıllı örnekleme yap
        
        Mantık:
        - Tüm kombinasyon türlerinden eşit oranda örnek al
        - Tüm zaman dilimlerinden eşit oranda örnek al
        - Rastgele örnekleme yapılır
        
        Args:
            strategies: Strateji listesi
            max_strategies: Maksimum strateji sayısı
            
        Returns:
            Örneklenmiş strateji listesi
        """
        if len(strategies) <= max_strategies:
            logger.info(f"Örnekleme gerekli değil ({len(strategies)} ≤ {max_strategies})")
            return strategies
        
        logger.info(f"Akıllı örnekleme başladı: {len(strategies)} -> {max_strategies}")
        
        # Combo size'a göre grupla
        by_combo_size = {}
        for strat in strategies:
            size = strat['combo_size']
            if size not in by_combo_size:
                by_combo_size[size] = []
            by_combo_size[size].append(strat)
        
        # Her grup için orantılı örnekleme
        sampled = []
        for combo_size, strats in by_combo_size.items():
            # Bu grubun oranı
            ratio = len(strats) / len(strategies)
            sample_size = max(1, int(max_strategies * ratio))
            
            # Rastgele örnek al
            indices = np.random.choice(len(strats), size=min(sample_size, len(strats)), replace=False)
            sampled.extend([strats[i] for i in indices])
        
        logger.info(f"Örnekleme tamamlandı: {len(sampled)} strateji")
        return sampled[:max_strategies]
    
    def cluster_indicators(self, num_clusters: int = 5) -> Dict[int, List[str]]:
        """
        İndikatörleri kümeleme yap (opsiyonel, ileri seviye)
        
        Benzer hareket eden indikatörleri gruplayıp,
        her gruptan 1-2 indikatör seç
        
        Args:
            num_clusters: Küme sayısı
            
        Returns:
            {küme_id: [indikatörler]}
        """
        logger.info(f"İndikatör kümeleme başladı ({num_clusters} küme)...")
        
        # Distance matrix hesapla
        distance_matrix = 1 - self.correlation_matrix.values.astype(float)
        
        # Kümeleme yap
        clustering = AgglomerativeClustering(
            n_clusters=num_clusters,
            linkage='ward'
        )
        labels = clustering.fit_predict(distance_matrix)
        
        # Kümeleri ayır
        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(self.correlation_matrix.columns[idx])
        
        logger.info(f"Kümeleme tamamlandı: {len(clusters)} küme")
        return clusters
    
    def get_strategy_summary(self) -> Dict:
        """
        Stratejilerin özeti
        
        Returns:
            Özet bilgisi
        """
        if not self.strategies:
            return {}
        
        df = pd.DataFrame(self.strategies)
        
        summary = {
            'total_strategies': len(self.strategies),
            'by_combo_size': df['combo_size'].value_counts().to_dict(),
            'by_timeframe': df['timeframe'].value_counts().to_dict(),
            'by_status': df['status'].value_counts().to_dict(),
        }
        
        return summary
    
    def export_strategies(self, filepath: str) -> None:
        """
        Stratejileri CSV'ye kaydet
        
        Args:
            filepath: Çıktı dosya yolu
        """
        if not self.strategies:
            logger.warning("Kaydedilecek strateji yok")
            return
        
        df = pd.DataFrame(self.strategies)
        # İndikatörleri string'e dönüştür
        df['indicators'] = df['indicators'].apply(lambda x: ', '.join(x))
        df.to_csv(filepath, index=False)
        logger.info(f"Stratejiler kaydedildi: {filepath}")
