"""
Paguro Boost - Cross-platform System Optimizer

A modern system optimization tool with retro GUI interface
that provides advanced RAM optimization, disk cleanup, startup
management, and performance monitoring.

Author: Paguro Team
Version: 2.0.0
License: MIT
"""

__version__ = "2.0.0"
__title__ = "Paguro Boost"
__description__ = "Cross-platform system optimizer with retro GUI interface"
__author__ = "Paguro Team"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Paguro Team"

# Version info tuple
VERSION_INFO = (2, 0, 0)

# Package metadata
PACKAGE_NAME = "paguro-boost"
PROJECT_URL = "https://github.com/paguro-team/paguro-boost"
DOCUMENTATION_URL = "https://paguroboost.readthedocs.io"
BUG_TRACKER_URL = "https://github.com/paguro-team/paguro-boost/issues"

# Feature flags
FEATURES = {
    "GUI_INTERFACE": True,
    "RAM_OPTIMIZATION": True,
    "DISK_OPTIMIZATION": True,
    "STARTUP_OPTIMIZATION": True,
    "METRICS_MONITORING": True,
    "RETRO_THEME": True,
    "CROSS_PLATFORM": True,
}

# Import main classes for easier access
from .app import SystemOptimizer
from .metrics import SystemMetrics

__all__ = [
    "__version__",
    "__title__", 
    "__description__",
    "__author__",
    "__license__",
    "VERSION_INFO",
    "FEATURES",
    "SystemOptimizer",
    "SystemMetrics",
]