"""Fixed - Main Entry Point

Hata handling ve güvenli import
"""

import sys
import logging
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Utils import
try:
    from src.utils import setup_logging, get_logger
    setup_logging(log_level='INFO')
    logger = get_logger(__name__)
except Exception as e:
    print(f"Logging setup error: {e}")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# PyQt5 import
try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError as e:
    logger.error(f"PyQt5 yüklenemedi: {e}")
    logger.info("PyQt5'i yüklemek için: pip install PyQt5")
    PYQT5_AVAILABLE = False

# GUI import
if PYQT5_AVAILABLE:
    try:
        from src.gui import MainWindow
        GUI_AVAILABLE = True
    except Exception as e:
        logger.error(f"GUI modülleri yüklenemedi: {e}", exc_info=True)
        GUI_AVAILABLE = False
else:
    GUI_AVAILABLE = False


def main():
    """Ana fonksiyon"""
    logger.info("="*60)
    logger.info("MT5 STRATEJİ TARAMA BOTU v0.1.0 BAŞLATILIYOR")
    logger.info("="*60)
    
    if not PYQT5_AVAILABLE:
        logger.error("PyQt5 yüklü değil!")
        logger.info("\nKurulum: pip install -r requirements.txt")
        return 1
    
    if not GUI_AVAILABLE:
        logger.error("GUI modülleri yüklenemedi!")
        return 1
    
    try:
        # PyQt5 uygulaması oluştur
        app = QApplication(sys.argv)
        
        # Ana pencereyi oluştur ve göster
        window = MainWindow()
        window.show()
        
        logger.info("Ana pencere açıldı")
        
        # Event loop'u başlat
        exit_code = app.exec_()
        
        logger.info(f"Uygulama sonlandırıldı (Kod: {exit_code})")
        return exit_code
        
    except Exception as e:
        logger.error(f"Uygulama hatası: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
