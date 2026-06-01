"""Test Script - Temel Fonksiyonları Test Et

Örnek:
  python test_basics.py
"""

import sys
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.mock_data import MockDataGenerator, MockStrategyResults
from src.utils import setup_logging, get_logger

# Logging setup
setup_logging(log_level='INFO')
logger = get_logger(__name__)


def test_mock_data():
    """Mock veri testı"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Mock OHLC Verisi")
    logger.info("="*60)
    
    try:
        df = MockDataGenerator.generate_sample_ohlc(num_candles=20)
        logger.info(f"✓ {len(df)} candle oluşturuldu")
        logger.info(f"  Sütunlar: {', '.join(df.columns)}")
        logger.info(f"  Tarih aralığı: {df.index[0]} ~ {df.index[-1]}")
        return True
    except Exception as e:
        logger.error(f"✗ Hata: {e}", exc_info=True)
        return False


def test_mock_results():
    """Mock sonuçlar testi"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Mock Strateji Sonuçları")
    logger.info("="*60)
    
    try:
        results = MockStrategyResults.generate_sample_results(5)
        logger.info(f"✓ {len(results)} strateji sonuçu oluşturuldu")
        
        passed = sum(1 for r in results if r['status'] == 'pass')
        failed = sum(1 for r in results if r['status'] == 'fail')
        logger.info(f"  Geçti: {passed} | Başarısız: {failed}")
        
        for r in results:
            status_icon = "✅" if r['status'] == 'pass' else "❌"
            logger.info(f"  {status_icon} {r['strategy_id']}: PF={r['profit_factor']}, WR={r['win_rate']:.1%}, DD={r['max_drawdown']:.1%}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Hata: {e}", exc_info=True)
        return False


def test_imports():
    """Import testleri"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Core Modülleri İmport Et")
    logger.info("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    modules = [
        ('src.core.data_loader', 'DataLoader'),
        ('src.core.indicator_engine', 'IndicatorEngine'),
        ('src.core.strategy_generator', 'StrategyGenerator'),
        ('src.core.backtest_engine', 'BacktestEngine'),
        ('src.core.risk_calculator', 'RiskCalculator'),
        ('src.core.metrics_calculator', 'MetricsCalculator'),
        ('src.core.stress_tester', 'StressTester'),
    ]
    
    for module_name, class_name in modules:
        tests_total += 1
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            logger.info(f"✓ {class_name} imported from {module_name}")
            tests_passed += 1
        except Exception as e:
            logger.warning(f"✗ {class_name} import failed: {e}")
    
    logger.info(f"\n  Sonuç: {tests_passed}/{tests_total} modül başarıyla loaded")
    return tests_passed == tests_total


def main():
    """Ana test fonksiyonu"""
    logger.info("""
╔═══════════════════════════════════════════════════════════╗
║   MT5 STRATEJİ TARAMA BOTU - TEMEL TESTLER             ║
║   v0.1.0 (BETA)                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'Mock Data': test_mock_data(),
        'Mock Results': test_mock_results(),
        'Imports': test_imports(),
    }
    
    logger.info("\n" + "="*60)
    logger.info("TEST SONUÇLARI")
    logger.info("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    logger.info(f"\nÖZET: {sum(results.values())}/{len(results)} test geçti")
    
    if all_passed:
        logger.info("\n🌟 Harika! Temel testler başarılı 🌟")
        logger.info("\nSonraki adım: python main.py")
        return 0
    else:
        logger.warning("\n⚠️ Bazı testler başarısız oldu")
        return 1


if __name__ == '__main__':
    sys.exit(main())
