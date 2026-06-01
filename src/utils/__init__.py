"""Utils Package - Fixed Initializer"""

import sys
from pathlib import Path

# Path ekle
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from .logger import setup_logging, get_logger
    print("✓ Logging utilities imported")
except ImportError as e:
    print(f"✗ Logging import error: {e}")
    setup_logging = None
    get_logger = None

try:
    from .mock_data import MockDataGenerator, MockStrategyResults
    print("✓ Mock data utilities imported")
except ImportError as e:
    print(f"✗ Mock data import error: {e}")
    MockDataGenerator = None
    MockStrategyResults = None

__all__ = [
    'setup_logging',
    'get_logger',
    'MockDataGenerator',
    'MockStrategyResults',
]
