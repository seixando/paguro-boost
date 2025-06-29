"""
Configuration settings for Paguro Boost
"""

import os
import platform
from pathlib import Path
from typing import Dict, Any

# Application configuration
APP_CONFIG = {
    "name": "Paguro Boost",
    "version": "2.0.0",
    "author": "Paguro Team",
    "description": "Cross-platform System Optimizer",
}

# System detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux" 
IS_WSL = "microsoft" in platform.uname().release.lower() if IS_LINUX else False

# Paths configuration
if IS_WINDOWS:
    DEFAULT_LOG_DIR = Path(os.environ.get("APPDATA", "")) / "PaguroBoost" / "logs"
    DEFAULT_DATA_DIR = Path(os.environ.get("APPDATA", "")) / "PaguroBoost" / "data"
    DEFAULT_CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / "PaguroBoost" / "config"
else:
    home = Path.home()
    DEFAULT_LOG_DIR = home / ".paguro-boost" / "logs"
    DEFAULT_DATA_DIR = home / ".paguro-boost" / "data"
    DEFAULT_CONFIG_DIR = home / ".paguro-boost" / "config"

# Create directories if they don't exist
for dir_path in [DEFAULT_LOG_DIR, DEFAULT_DATA_DIR, DEFAULT_CONFIG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# File paths
LOG_FILE = DEFAULT_LOG_DIR / "paguro_boost.log"
METRICS_FILE = DEFAULT_DATA_DIR / "system_metrics.json"
CONFIG_FILE = DEFAULT_CONFIG_DIR / "settings.json"

# GUI Configuration
GUI_CONFIG = {
    "theme": "retro",
    "colors": {
        "background": "#000000",
        "foreground": "#00ff00",
        "accent": "#ffff00",
        "warning": "#ffaa00",
        "error": "#ff0000",
    },
    "fonts": {
        "main": ("Courier", 10),
        "title": ("Courier", 16, "bold"),
        "subtitle": ("Courier", 10),
    },
    "update_interval": 2000,  # milliseconds
    "window_size": (800, 600),
    "window_resizable": True,
}

# Optimization settings
OPTIMIZATION_CONFIG = {
    "ram": {
        "cleanup_cache": True,
        "optimize_working_sets": True,
        "clear_dns_cache": True,
        "analyze_processes": True,
    },
    "disk": {
        "clean_temp_files": True,
        "clean_old_files": True,
        "days_threshold": 30,
        "analyze_duplicates": True,
        "defragment_on_windows": False,  # Safe default
    },
    "startup": {
        "analyze_programs": True,
        "classify_importance": True,
        "estimate_boot_time": True,
        "auto_optimize": False,  # Require user confirmation
    },
    "monitoring": {
        "collect_metrics": True,
        "update_interval": 30,  # seconds
        "history_retention_days": 7,
        "max_samples": 1000,
    },
}

# Safety settings
SAFETY_CONFIG = {
    "require_confirmation": True,
    "backup_before_changes": True,
    "log_all_operations": True,
    "safe_mode": True,
    "max_file_size_mb": 100,  # Don't process files larger than this
    "excluded_directories": [
        # Windows
        "C:\\Windows\\System32",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        # Linux
        "/bin", "/sbin", "/usr/bin", "/usr/sbin",
        "/etc", "/sys", "/proc", "/dev",
    ],
}

# Performance settings
PERFORMANCE_CONFIG = {
    "max_threads": 4,
    "chunk_size": 1024 * 1024,  # 1MB chunks for file operations
    "timeout_seconds": 30,
    "memory_limit_mb": 512,
    "enable_caching": True,
}

# Export all configurations
CONFIG: Dict[str, Any] = {
    "app": APP_CONFIG,
    "gui": GUI_CONFIG,
    "optimization": OPTIMIZATION_CONFIG,
    "safety": SAFETY_CONFIG,
    "performance": PERFORMANCE_CONFIG,
    "paths": {
        "log_dir": str(DEFAULT_LOG_DIR),
        "data_dir": str(DEFAULT_DATA_DIR),
        "config_dir": str(DEFAULT_CONFIG_DIR),
        "log_file": str(LOG_FILE),
        "metrics_file": str(METRICS_FILE),
        "config_file": str(CONFIG_FILE),
    },
    "system": {
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX,
        "is_wsl": IS_WSL,
        "platform": platform.system(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
    },
}

def get_config(section: str = None) -> Dict[str, Any]:
    """Get configuration section or entire config."""
    if section:
        return CONFIG.get(section, {})
    return CONFIG

def update_config(section: str, key: str, value: Any) -> None:
    """Update configuration value."""
    if section in CONFIG:
        CONFIG[section][key] = value

def save_config() -> None:
    """Save current configuration to file."""
    import json
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=2, default=str)
    except Exception as e:
        print(f"Warning: Could not save config: {e}")

def load_config() -> None:
    """Load configuration from file."""
    import json
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                saved_config = json.load(f)
                CONFIG.update(saved_config)
    except Exception as e:
        print(f"Warning: Could not load config: {e}")

# Auto-load config on import
load_config()