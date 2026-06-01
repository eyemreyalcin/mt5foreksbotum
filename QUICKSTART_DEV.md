# Hızlı Başlangıç Kılavuzu - Geliştirici Versiyonu

## 🚀 Kurulum

### 1. Depoyu klonla
```bash
git clone https://github.com/eyemreyalcin/mt5foreksbotum.git
cd mt5foreksbotum
```

### 2. Sanal ortam (venv) oluştur
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları yükle
```bash
pip install -r requirements.txt
```

## 🧪 Testler

### Temel testleri çalıştır
```bash
python test_basics.py
```

Bu şunları test eder:
- ✓ Mock veri üretimi
- ✓ Mock sonuçları
- ✓ Core modülü importları

## 🎮 Uygulamayı Başlat

```bash
python main.py
```

## 📁 Veri Hazırlama

1. MT5'ten CSV olarak OHLC verisi dışa aktar
2. `data/raw/` klasörüne yerleştir
3. Format: `Time,Open,High,Low,Close,Volume`

### Örnek:
```csv
Time,Open,High,Low,Close,Volume
2014.01.01 00:00,1.3750,1.3800,1.3720,1.3795,1000
2014.01.01 01:00,1.3795,1.3850,1.3790,1.3820,950
```

## 📊 Kullanım Adımları

### ADIM 1: Veri Yükle
1. GUI'de "Dosya Seç" butonuna tıkla
2. CSV dosyasını seç
3. Veri bilgilerini kontrol et

### ADIM 2: Ayarları Yapılandır
1. Filtreleme kriterlerini ayarla:
   - Min Profit Factor: 1.5
   - Min Win Rate: %60
   - Max Drawdown: %15

2. İndikatör ayarları:
   - Kombinasyon tipleri: 2'li, 3'lü, 4'lü
   - Korelasyon limiti: 0.70

3. Test ayarları:
   - Walk Forward: Aktif
   - Stress Test: Aktif
   - Monte Carlo: 1000 run

### ADIM 3: Taramayı Başlat
1. "TARAMAYI BAŞLAT" butonuna tıkla
2. İlerleme barını izle
3. Sonuçları tablodan gözle

## 🎯 Sonuçları Anlama

### Yeşil (✅ GEÇTİ):
- Tüm filtreleri sağlıyor
- Backtest başarılı
- Demo hesapta test edilebilir

### Kırmızı (❌ BAŞARISIZ):
- Filtreleri sağlamıyor
- Daha fazla test gerekli
- İyileştirme gerekebilir

## 📈 Strateji Detayları

Bir strateji seç → "Detay Aç" butonuna tıkla

Görebilecekleriniz:
- 💰 Para metrikleri
- 📊 İşlem metrikleri
- ⚠️ Risk metrikleri
- 📋 Trade günlüğü
- 🧪 Stress test sonuçları

## ⚠️ Önemli Uyarılar

- **Geçmiş performans gelecek sonuçlarını garantilemez!**
- Her zaman demo hesapta uzun dönem test yapın
- Canlı işlem yapmadan önce çok dikkatli testler yapın
- Pazar koşulları değiştiğinde strateji başarısız olabilir

## 🐛 Hata Raporlama

```bash
# Log dosyası konumu:
logs/bot.log

# GitHub'da issue açın:
https://github.com/eyemreyalcin/mt5foreksbotum/issues
```

## 💡 İpuçları

1. En az 3 yıllık veri kullan
2. Sadece likit enstrümanları test et (EUR/USD, GBP/USD, vb)
3. Walk Forward test'i aktif tut
4. Stress test sonuçlarına dikkat et
5. Birden fazla strateji kombinlemeyi düşün

## 📚 Kaynaklar

- [Teknik Analiz](https://www.investopedia.com/)
- [Risk Yönetimi](https://en.wikipedia.org/wiki/Risk_management)
- [Backtesting](https://en.wikipedia.org/wiki/Backtesting)

## 📞 Destek

- **GitHub:** [eyemreyalcin](https://github.com/eyemreyalcin)
- **Issues:** Sorun raporu için GitHub Issues kullanın

---

**Versiyon:** 0.1.0 (BETA)  
**Güncelleme:** 2026-06-01
