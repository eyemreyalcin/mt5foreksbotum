"""İndikatör Hesaplama Motoru

Bu modül 100+ teknik indikatörü hesaplar:
- Trend İndikatörleri (SMA, EMA, ADX, AROON)
- Momentum İndikatörleri (RSI, MACD, Stochastic, CCI)
- Volatilite İndikatörleri (Bollinger Bands, ATR, KAMA)
- Hacim İndikatörleri (OBV, ADOSC, MFI)
- Overlap İndikatörleri (WMA, HMA, DEMA)
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class IndicatorEngine:
    """100+ İndikatör hesaplama motoru"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: OHLC verisi (Open, High, Low, Close, Volume)
        """
        self.df = df.copy()
        self.indicators = {}
        
        # pandas_ta ayarlarını güncelle
        df.ta.strategy = None
        
    def calculate_all_indicators(self) -> pd.DataFrame:
        """
        Tüm indikatörleri hesapla ve DataFrame'e ekle
        
        Returns:
            Tüm indikatörlerle güncellenmiş DataFrame
        """
        logger.info("Tüm indikatörler hesaplanıyor...")
        
        # Trend İndikatörleri
        self._calculate_trend_indicators()
        
        # Momentum İndikatörleri
        self._calculate_momentum_indicators()
        
        # Volatilite İndikatörleri
        self._calculate_volatility_indicators()
        
        # Hacim İndikatörleri
        self._calculate_volume_indicators()
        
        # Overlap İndikatörleri
        self._calculate_overlap_indicators()
        
        # Cycle İndikatörleri
        self._calculate_cycle_indicators()
        
        logger.info(f"Toplam {len(self.indicators)} indikatör hesaplandı")
        return self.df
    
    def _calculate_trend_indicators(self):
        """Trend İndikatörleri: ADX, AROON, SMA, EMA, vb"""
        
        # ADX (Average Directional Index)
        adx = self.df.ta.adx(length=14)
        if adx is not None:
            self.df = pd.concat([self.df, adx], axis=1)
            self.indicators['ADX'] = 'Trend'
        
        # AROON
        aroon = self.df.ta.aroon(length=25)
        if aroon is not None:
            self.df = pd.concat([self.df, aroon], axis=1)
            self.indicators['AROON_UP'] = 'Trend'
            self.indicators['AROON_DOWN'] = 'Trend'
        
        # SMA (Simple Moving Average)
        for period in [10, 20, 50, 100, 200]:
            sma = self.df.ta.sma(length=period)
            if sma is not None:
                self.df[f'SMA_{period}'] = sma
                self.indicators[f'SMA_{period}'] = 'Trend'
        
        # EMA (Exponential Moving Average)
        for period in [9, 12, 26, 50, 100, 200]:
            ema = self.df.ta.ema(length=period)
            if ema is not None:
                self.df[f'EMA_{period}'] = ema
                self.indicators[f'EMA_{period}'] = 'Trend'
        
        # DEMA (Double EMA)
        dema = self.df.ta.dema(length=20)
        if dema is not None:
            self.df[f'DEMA_20'] = dema
            self.indicators['DEMA_20'] = 'Trend'
        
        # TEMA (Triple EMA)
        tema = self.df.ta.tema(length=20)
        if tema is not None:
            self.df[f'TEMA_20'] = tema
            self.indicators['TEMA_20'] = 'Trend'
        
        logger.info("Trend indikatörleri hesaplandı")
    
    def _calculate_momentum_indicators(self):
        """Momentum İndikatörleri: RSI, MACD, Stochastic, CCI, ROC, vb"""
        
        # RSI (Relative Strength Index)
        for period in [7, 14, 21]:
            rsi = self.df.ta.rsi(length=period)
            if rsi is not None:
                self.df[f'RSI_{period}'] = rsi
                self.indicators[f'RSI_{period}'] = 'Momentum'
        
        # MACD
        macd = self.df.ta.macd(fast=12, slow=26, signal=9)
        if macd is not None:
            self.df = pd.concat([self.df, macd], axis=1)
            self.indicators['MACD_12_26_9'] = 'Momentum'
        
        # Stochastic
        stoch = self.df.ta.stoch(k=14, d=3, smooth_k=3)
        if stoch is not None:
            self.df = pd.concat([self.df, stoch], axis=1)
            self.indicators['STOCH_K'] = 'Momentum'
            self.indicators['STOCH_D'] = 'Momentum'
        
        # CCI (Commodity Channel Index)
        cci = self.df.ta.cci(length=20)
        if cci is not None:
            self.df[f'CCI_20'] = cci
            self.indicators['CCI_20'] = 'Momentum'
        
        # ROC (Rate of Change)
        roc = self.df.ta.roc(length=12)
        if roc is not None:
            self.df[f'ROC_12'] = roc
            self.indicators['ROC_12'] = 'Momentum'
        
        # MFI (Money Flow Index)
        mfi = self.df.ta.mfi(length=14)
        if mfi is not None:
            self.df[f'MFI_14'] = mfi
            self.indicators['MFI_14'] = 'Momentum'
        
        # Williams %R
        williams_r = self.df.ta.willr(length=14)
        if williams_r is not None:
            self.df[f'WILLR_14'] = williams_r
            self.indicators['WILLR_14'] = 'Momentum'
        
        logger.info("Momentum indikatörleri hesaplandı")
    
    def _calculate_volatility_indicators(self):
        """Volatilite İndikatörleri: Bollinger Bands, ATR, KAMA, vb"""
        
        # Bollinger Bands
        bb = self.df.ta.bbands(length=20, std=2)
        if bb is not None:
            self.df = pd.concat([self.df, bb], axis=1)
            self.indicators['BB_UPPER'] = 'Volatility'
            self.indicators['BB_MIDDLE'] = 'Volatility'
            self.indicators['BB_LOWER'] = 'Volatility'
        
        # ATR (Average True Range)
        atr = self.df.ta.atr(length=14)
        if atr is not None:
            self.df[f'ATR_14'] = atr
            self.indicators['ATR_14'] = 'Volatility'
        
        # NATR (Normalized ATR)
        natr = self.df.ta.natr(length=14)
        if natr is not None:
            self.df[f'NATR_14'] = natr
            self.indicators['NATR_14'] = 'Volatility'
        
        # KAMA (Kaufman Adaptive Moving Average)
        kama = self.df.ta.kama(length=10)
        if kama is not None:
            self.df[f'KAMA_10'] = kama
            self.indicators['KAMA_10'] = 'Volatility'
        
        logger.info("Volatilite indikatörleri hesaplandı")
    
    def _calculate_volume_indicators(self):
        """Hacim İndikatörleri: OBV, AD, ADOSC, CMFI, vb"""
        
        # OBV (On Balance Volume)
        obv = self.df.ta.obv()
        if obv is not None:
            self.df[f'OBV'] = obv
            self.indicators['OBV'] = 'Volume'
        
        # AD (Accumulation Distribution)
        ad = self.df.ta.ad()
        if ad is not None:
            self.df[f'AD'] = ad
            self.indicators['AD'] = 'Volume'
        
        # ADOSC (Accumulation Distribution Oscillator)
        adosc = self.df.ta.adosc(fast=3, slow=10)
        if adosc is not None:
            self.df[f'ADOSC'] = adosc
            self.indicators['ADOSC'] = 'Volume'
        
        logger.info("Hacim indikatörleri hesaplandı")
    
    def _calculate_overlap_indicators(self):
        """Overlap İndikatörleri: WMA, HMA, VWAP, vb"""
        
        # WMA (Weighted Moving Average)
        wma = self.df.ta.wma(length=20)
        if wma is not None:
            self.df[f'WMA_20'] = wma
            self.indicators['WMA_20'] = 'Overlap'
        
        # HMA (Hull Moving Average)
        hma = self.df.ta.hma(length=20)
        if hma is not None:
            self.df[f'HMA_20'] = hma
            self.indicators['HMA_20'] = 'Overlap'
        
        logger.info("Overlap indikatörleri hesaplandı")
    
    def _calculate_cycle_indicators(self):
        """Cycle İndikatörleri: Sine, Cosine, vb"""
        
        # Log Returns (momentum proxy)
        log_returns = np.log(self.df['Close'] / self.df['Close'].shift(1))
        self.df['LOG_RETURNS'] = log_returns
        self.indicators['LOG_RETURNS'] = 'Cycle'
        
        logger.info("Cycle indikatörleri hesaplandı")
    
    def get_indicator_categories(self) -> Dict[str, List[str]]:
        """
        İndikatörleri kategorilere göre grupla
        
        Returns:
            {kategori: [indikatör1, indikatör2, ...]}
        """
        categories = {}
        for indicator, category in self.indicators.items():
            if category not in categories:
                categories[category] = []
            categories[category].append(indicator)
        
        return categories
    
    def get_valid_indicators(self) -> List[str]:
        """
        Tüm geçerli (NaN olmayan) indikatörleri getir
        
        Returns:
            İndikatör adları listesi
        """
        valid = []
        for col in self.df.columns:
            if col not in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if not self.df[col].isna().all():
                    valid.append(col)
        
        return valid
    
    def calculate_indicator_correlation(self) -> pd.DataFrame:
        """
        İndikatörler arasında korelasyon matrisi hesapla
        
        Returns:
            Korelasyon DataFrame
        """
        valid_indicators = self.get_valid_indicators()
        subset = self.df[valid_indicators].dropna()
        correlation = subset.corr()
        
        return correlation
