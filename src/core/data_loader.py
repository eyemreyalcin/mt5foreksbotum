"""Veri Yükleme ve İşleme Modülü

Bu modül CSV dosyalarından OHLC verisi yükler ve işler.
- MT5 uyumlu CSV format desteği
- Veri temizleme ve doğrulama
- Zaman dilimi dönüştürme (H1, H4, D1, vb)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataLoader:
    """OHLC verisi yükleme ve işleme"""
    
    def __init__(self, data_dir: str = 'data/raw'):
        """
        Args:
            data_dir: CSV dosyalarının bulunduğu dizin
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_csv(self, file_path: str, 
                 datetime_column: str = 'Time',
                 date_format: str = '%Y.%m.%d %H:%M') -> pd.DataFrame:
        """
        CSV dosyasından OHLC verisi yükle
        
        Args:
            file_path: CSV dosya yolu
            datetime_column: Tarih saat sütun adı
            date_format: Tarih format string
            
        Returns:
            OHLC DataFrame
            
        Örnek:
            >>> loader = DataLoader()
            >>> df = loader.load_csv('data/raw/EURUSD_H1.csv')
            >>> print(df.head())
        """
        try:
            df = pd.read_csv(file_path)
            
            # Tarih sütununu datetime'a dönüştür
            if datetime_column in df.columns:
                df[datetime_column] = pd.to_datetime(
                    df[datetime_column], 
                    format=date_format,
                    errors='coerce'
                )
                df.set_index(datetime_column, inplace=True)
            
            # Gerekli sütunları kontrol et
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing = [col for col in required_columns if col not in df.columns]
            
            if missing:
                logger.warning(f"Eksik sütunlar: {missing}")
            
            # Sütun adlarını standartlaştır
            df.columns = df.columns.str.capitalize()
            
            logger.info(f"Veri yüklendi: {len(df)} satır, {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        OHLC veri kalitesini kontrol et
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Boş veriler
        if df.empty:
            issues.append("DataFrame boş")
        
        # NaN kontrol
        nan_cols = df.columns[df.isna().any()].tolist()
        if nan_cols:
            issues.append(f"NaN değerler bulundu: {nan_cols}")
        
        # OHLC mantık kontrol
        if 'High' in df.columns and 'Low' in df.columns:
            if (df['High'] < df['Low']).any():
                issues.append("High < Low olan satırlar var")
        
        # Negatif fiyat kontrol
        price_cols = ['Open', 'High', 'Low', 'Close']
        for col in price_cols:
            if col in df.columns and (df[col] < 0).any():
                issues.append(f"Negatif fiyatlar bulundu: {col}")
        
        # Hacim kontrol
        if 'Volume' in df.columns and (df['Volume'] < 0).any():
            issues.append("Negatif volume bulundu")
        
        return len(issues) == 0, issues
    
    def resample_timeframe(self, df: pd.DataFrame, 
                          from_timeframe: str = '1H',
                          to_timeframe: str = '4H') -> pd.DataFrame:
        """
        Zaman dilimini değiştir (örn H1 -> H4)
        
        Args:
            df: OHLC DataFrame (datetime index gerekli)
            from_timeframe: Kaynak zaman dilimi
            to_timeframe: Hedef zaman dilimi
            
        Returns:
            Yeni zaman diliminde DataFrame
            
        Örnek:
            >>> df_h1 = loader.load_csv('EURUSD_H1.csv')
            >>> df_h4 = loader.resample_timeframe(df_h1, '1H', '4H')
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            logger.error("Index datetime olmmalı")
            return df
        
        resampled = pd.DataFrame()
        resampled['Open'] = df['Open'].resample(to_timeframe).first()
        resampled['High'] = df['High'].resample(to_timeframe).max()
        resampled['Low'] = df['Low'].resample(to_timeframe).min()
        resampled['Close'] = df['Close'].resample(to_timeframe).last()
        resampled['Volume'] = df['Volume'].resample(to_timeframe).sum()
        
        # NaN'leri kaldır
        resampled = resampled.dropna()
        
        logger.info(f"Zaman dilimi değiştirildi: {from_timeframe} -> {to_timeframe}")
        return resampled
    
    def split_data(self, df: pd.DataFrame, 
                   train_ratio: float = 0.7,
                   val_ratio: float = 0.15) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Veriyi train/validation/test'e böl
        
        Args:
            df: OHLC DataFrame
            train_ratio: Eğitim veri oranı (0.7 = %70)
            val_ratio: Validation veri oranı (0.15 = %15)
            
        Returns:
            (train_df, val_df, test_df)
        """
        n = len(df)
        train_size = int(n * train_ratio)
        val_size = int(n * val_ratio)
        
        train_df = df.iloc[:train_size]
        val_df = df.iloc[train_size:train_size + val_size]
        test_df = df.iloc[train_size + val_size:]
        
        logger.info(f"Veri bölündü - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        return train_df, val_df, test_df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Duplicate candle'ları kaldır
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            Temiz DataFrame
        """
        before = len(df)
        df = df[~df.index.duplicated(keep='first')]
        after = len(df)
        
        if before > after:
            logger.warning(f"Duplicate candle'lar kaldırıldı: {before - after}")
        
        return df
    
    def handle_missing_candles(self, df: pd.DataFrame, 
                              timeframe: str = '1H') -> pd.DataFrame:
        """
        Eksik candle'ları (gaps) doldur
        
        Args:
            df: OHLC DataFrame
            timeframe: Zaman dilimi
            
        Returns:
            Doldurulan DataFrame
        """
        # Boş tarihler için row ekle
        df = df.asfreq(timeframe, method='pad')
        
        # Forward fill ile eksik değerleri doldur
        df['Open'] = df['Open'].fillna(method='pad')
        df['High'] = df['High'].fillna(method='pad')
        df['Low'] = df['Low'].fillna(method='pad')
        df['Close'] = df['Close'].fillna(method='pad')
        df['Volume'] = df['Volume'].fillna(0)
        
        logger.info(f"Eksik candle'lar dolduruldu")
        return df
    
    def get_available_symbols(self) -> List[str]:
        """
        Veri dizininde bulunan tüm sembolleri getir
        
        Returns:
            Sembol listesi
        """
        csv_files = list(self.data_dir.glob('*.csv'))
        symbols = [f.stem for f in csv_files]
        return sorted(symbols)
    
    def get_date_range(self, df: pd.DataFrame) -> Tuple[datetime, datetime]:
        """
        DataFrame'in tarih aralığını getir
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            (start_date, end_date)
        """
        if isinstance(df.index, pd.DatetimeIndex):
            return df.index[0], df.index[-1]
        return None, None
