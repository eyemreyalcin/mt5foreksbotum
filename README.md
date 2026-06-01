# MT5 Strateji Tarama Botu 🤖

Türkçe MT5 uyumlu, yapay zeka destekli strateji üretim ve backtesting platformu.

## 🎯 Özellikler

- ✅ **100+ İndikatör/Osilatör**: Trend, Momentum, Volatility, Volume, Overlap
- ✅ **Otonom Strateji Taraması**: 2'li, 3'lü, 4'lü indikatör kombinasyonları
- ✅ **Dual Zaman Dilimi**: H1 ve H4 simultane analiz
- ✅ **Akıllı Risk Yönetimi**: Per-trade %2 risk ile position sizing
- ✅ **Kapsamlı Backtesting**: Geçmiş verilerle test etme
- ✅ **Walk Forward Test**: İleri dönük simülasyon
- ✅ **Stress Testing**: Monte Carlo + Scenario Analysis
- ✅ **Profesyonel Raporlama**: Anlaşılır GUI ve rapor çıkışı
- ✅ **Lokal Çalıştırma**: Masaüstünde tamamen offline işlem

## 📋 Kritik Filtreleme Kriterleri

Stratejiler şu kriterlerden geçmeli:

| Metrik | Minimum | Açıklama |
|--------|---------|----------|
| **Profit Factor** | 1.5x | Kazançlar / Kayıplar oranı |
| **Win Rate** | 60% | Kazanan işlemler oranı |
| **Max Drawdown** | ≤15% | Zirveye kadar maksimum düşüş |
| **Sharpe Ratio** | ≥0.8 | Risk ayarlı getiri |
| **Sortino Ratio** | ≥1.0 | Olumsuz volatilite dikkate |

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.8+
- pip (Python paket yöneticisi)

### 2. Depoyu klonla

```bash
git clone https://github.com/eyemreyalcin/mt5foreksbotum.git
cd mt5foreksbotum
```

### 3. Sanal ortam oluştur

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

## 📊 Veri Hazırlama

1. MT5'ten OHLC verilerini CSV olarak dışa aktar
2. `data/raw/` dizinine yerleştir
3. CSV formatı: Time, Open, High, Low, Close, Volume

**Örnek:**
```
Time,Open,High,Low,Close,Volume
2014.01.01 00:00,1.3750,1.3800,1.3720,1.3795,1000
2014.01.01 01:00,1.3795,1.3850,1.3790,1.3820,950
...
```

## 🎮 Kullanım

### GUI'yi Başlat

```bash
python main.py
```

### Arayüz

**ADIM 1:** Veri Yükle
- 📁 CSV dosyasını seç
- Veri bilgilerini kontrol et

**ADIM 2:** Ayarları Yapılandır
- Filtreleme kriterleri
- İndikatör ayarları
- Test ayarları

**ADIM 3:** Taramayı Başlat
- ▶ Taramayı başlat
- İlerlemeyi izle
- Sonuçları gör

## 📈 Raporlama

Bir strateji için şunlar oluşturulur:

- 📊 Equity Curve (Bakiye Zaman Serisi)
- 📉 Drawdown Grafiği
- 📋 Detaylı Performans Metrikleri
- 🔬 Stress Test Sonuçları
- 📊 Walk Forward Analizi
- 📥 CSV/JSON Export

## 📁 Dizin Yapısı

```
mt5foreksbotum/
├── data/
│   ├── raw/              # MT5'ten dışa aktarılan CSV dosyaları
│   └── processed/        # İşlenmiş veriler
├── src/
│   ├── core/             # Ana işlem modülleri
│   ├── gui/              # PyQt5 arayüzü
│   └── utils/            # Yardımcı fonksiyonlar
├── results/              # Backtest sonuçları
├── logs/                 # Uygulama logları
├── main.py               # GUI entry point
├── requirements.txt      # Bağımlılıklar
├── config.yaml           # Ayarlar
├── README.md             # Bu dosya
└── QUICKSTART.md         # Başlangıç rehberi
```

## ⚠️ Uyarı

**Geçmiş performans gelecek sonuçları garantilemez!** 

Bu araç eğitim ve araştırma amaçlıdır. Gerçek para ile işlem yapmadan önce mutlaka demo hesapta uzun süreli test yapın.

## 📚 Kaynaklar

- [Teknik Analiz](https://www.investopedia.com/)
- [Risk Yönetimi](https://en.wikipedia.org/wiki/Risk_management)
- [Backtesting](https://en.wikipedia.org/wiki/Backtesting)

## 📞 İletişim

- **GitHub:** [eyemreyalcin](https://github.com/eyemreyalcin)
- **Issues:** Sorun raporu için GitHub Issues kullanın

---

**Versiyon:** 0.1.0 (BETA)  
**Güncelleme:** 2026-06-01  
**Lisans:** MIT
