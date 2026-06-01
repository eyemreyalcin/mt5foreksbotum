"""Fixed - GUI Package Initializer

GUI modüller güvenli import
"""

import sys
from pathlib import Path

# Path ekle
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from .utils import (
        NumberFormatter,
        ColorScheme,
        StatusMessages,
        ValidationRules,
        ProgressTracker,
    )
    print("✓ GUI utilities imported")
except ImportError as e:
    print(f"✗ GUI utilities import error: {e}")
    NumberFormatter = None
    ColorScheme = None
    StatusMessages = None
    ValidationRules = None
    ProgressTracker = None

try:
    from .import_panel import ImportPanel
    print("✓ ImportPanel imported")
except ImportError as e:
    print(f"✗ ImportPanel import error: {e}")
    ImportPanel = None

try:
    from .settings_panel import SettingsPanel
    print("✓ SettingsPanel imported")
except ImportError as e:
    print(f"✗ SettingsPanel import error: {e}")
    SettingsPanel = None

try:
    from .results_panel import ResultsPanel
    print("✓ ResultsPanel imported")
except ImportError as e:
    print(f"✗ ResultsPanel import error: {e}")
    ResultsPanel = None

try:
    from .detail_window import StrategyDetailWindow
    print("✓ StrategyDetailWindow imported")
except ImportError as e:
    print(f"✗ StrategyDetailWindow import error: {e}")
    StrategyDetailWindow = None

try:
    from .main_window import MainWindow
    print("✓ MainWindow imported")
except ImportError as e:
    print(f"✗ MainWindow import error: {e}")
    MainWindow = None

__all__ = [
    'MainWindow',
    'ImportPanel',
    'SettingsPanel',
    'ResultsPanel',
    'StrategyDetailWindow',
    'NumberFormatter',
    'ColorScheme',
    'StatusMessages',
    'ValidationRules',
    'ProgressTracker',
]
