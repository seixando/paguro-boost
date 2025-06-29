"""
Professional logging configuration for Paguro Boost
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from .config import CONFIG, LOG_FILE

class PaguroLogger:
    """Professional logging class for Paguro Boost."""
    
    def __init__(self, name: str = "paguro_boost", level: str = "INFO"):
        self.name = name
        self.level = getattr(logging, level.upper())
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # Error handler (stderr for errors)
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger."""
        return self.logger
    
    def set_level(self, level: str) -> None:
        """Change logging level."""
        new_level = getattr(logging, level.upper())
        self.logger.setLevel(new_level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(new_level)
    
    @staticmethod
    def get_system_logger(component: str = "system") -> logging.Logger:
        """Get a logger for system operations."""
        logger_name = f"paguro_boost.{component}"
        logger = PaguroLogger(logger_name)
        return logger.get_logger()
    
    @staticmethod
    def get_gui_logger() -> logging.Logger:
        """Get a logger for GUI operations."""
        return PaguroLogger.get_system_logger("gui")
    
    @staticmethod
    def get_metrics_logger() -> logging.Logger:
        """Get a logger for metrics operations."""
        return PaguroLogger.get_system_logger("metrics")
    
    @staticmethod
    def get_optimizer_logger() -> logging.Logger:
        """Get a logger for optimizer operations."""
        return PaguroLogger.get_system_logger("optimizer")

# Global logger instances
main_logger = PaguroLogger()
system_logger = main_logger.get_logger()

# Export functions for easy use
def get_logger(name: str = "paguro_boost") -> logging.Logger:
    """Get a logger instance."""
    return PaguroLogger(name).get_logger()

def log_system_info() -> None:
    """Log system information at startup."""
    logger = get_logger("startup")
    
    system_info = CONFIG["system"]
    logger.info("=" * 60)
    logger.info("PAGURO BOOST v2.0 - SYSTEM STARTUP")
    logger.info("=" * 60)
    logger.info(f"Platform: {system_info['platform']}")
    logger.info(f"Architecture: {system_info['architecture']}")
    logger.info(f"Python Version: {system_info['python_version']}")
    logger.info(f"Is Windows: {system_info['is_windows']}")
    logger.info(f"Is Linux: {system_info['is_linux']}")
    logger.info(f"Is WSL: {system_info['is_wsl']}")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info("=" * 60)

def log_operation(operation: str, details: str = "", success: bool = True) -> None:
    """Log an operation with standardized format."""
    logger = get_logger("operations")
    
    status = "SUCCESS" if success else "FAILED"
    emoji = "✅" if success else "❌"
    
    message = f"{emoji} {operation.upper()}: {status}"
    if details:
        message += f" | {details}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)

def log_performance(operation: str, duration: float, details: str = "") -> None:
    """Log performance metrics."""
    logger = get_logger("performance")
    
    message = f"⏱️ PERFORMANCE | {operation}: {duration:.3f}s"
    if details:
        message += f" | {details}"
    
    logger.info(message)

# Configure root logger to avoid duplicate messages
logging.getLogger().handlers.clear()
logging.basicConfig(level=logging.WARNING)  # Only show warnings from other libraries