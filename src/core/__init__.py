"""Fixed - Core Modüler İnit

Tüm core modüllerin başarılı import edilebilmesi için
"""

import sys
from pathlib import Path

# Path ekle
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from .data_loader import DataLoader
    print("✓ DataLoader imported")
except ImportError as e:
    print(f"✗ DataLoader import error: {e}")
    DataLoader = None

try:
    from .indicator_engine import IndicatorEngine
    print("✓ IndicatorEngine imported")
except ImportError as e:
    print(f"✗ IndicatorEngine import error: {e}")
    IndicatorEngine = None

try:
    from .strategy_generator import StrategyGenerator
    print("✓ StrategyGenerator imported")
except ImportError as e:
    print(f"✗ StrategyGenerator import error: {e}")
    StrategyGenerator = None

try:
    from .backtest_engine import BacktestEngine
    print("✓ BacktestEngine imported")
except ImportError as e:
    print(f"✗ BacktestEngine import error: {e}")
    BacktestEngine = None

try:
    from .risk_calculator import RiskCalculator
    print("✓ RiskCalculator imported")
except ImportError as e:
    print(f"✗ RiskCalculator import error: {e}")
    RiskCalculator = None

try:
    from .metrics_calculator import MetricsCalculator
    print("✓ MetricsCalculator imported")
except ImportError as e:
    print(f"✗ MetricsCalculator import error: {e}")
    MetricsCalculator = None

try:
    from .stress_tester import StressTester
    print("✓ StressTester imported")
except ImportError as e:
    print(f"✗ StressTester import error: {e}")
    StressTester = None

__all__ = [
    'DataLoader',
    'IndicatorEngine',
    'StrategyGenerator',
    'BacktestEngine',
    'RiskCalculator',
    'MetricsCalculator',
    'StressTester',
]
