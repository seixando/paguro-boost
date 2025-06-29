"""
Custom exceptions for Paguro Boost
"""

class PaguroBoostException(Exception):
    """Base exception for Paguro Boost."""
    pass

class SystemOptimizationError(PaguroBoostException):
    """Raised when system optimization fails."""
    pass

class RAMOptimizationError(SystemOptimizationError):
    """Raised when RAM optimization fails."""
    pass

class DiskOptimizationError(SystemOptimizationError):
    """Raised when disk optimization fails."""
    pass

class StartupOptimizationError(SystemOptimizationError):
    """Raised when startup optimization fails."""
    pass

class MetricsError(PaguroBoostException):
    """Raised when metrics collection fails."""
    pass

class ConfigurationError(PaguroBoostException):
    """Raised when configuration is invalid."""
    pass

class GUIError(PaguroBoostException):
    """Raised when GUI operations fail."""
    pass

class UnsupportedPlatformError(PaguroBoostException):
    """Raised when platform is not supported."""
    pass

class InsufficientPermissionsError(PaguroBoostException):
    """Raised when insufficient permissions for operation."""
    pass

class SafetyError(PaguroBoostException):
    """Raised when safety checks fail."""
    pass

# Exception handling decorator
def handle_exceptions(logger=None, reraise=False):
    """Decorator to handle exceptions gracefully."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PaguroBoostException as e:
                if logger:
                    logger.error(f"Paguro Boost error in {func.__name__}: {e}")
                if reraise:
                    raise
                return None
            except Exception as e:
                if logger:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                if reraise:
                    raise PaguroBoostException(f"Unexpected error: {e}")
                return None
        return wrapper
    return decorator