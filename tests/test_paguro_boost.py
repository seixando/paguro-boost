"""
Unit tests for Paguro Boost
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import modules to test
from paguro_boost.app import SystemOptimizer
from paguro_boost.metrics import SystemMetrics
from paguro_boost.config import CONFIG
from paguro_boost.logger import get_logger


class TestSystemOptimizer(unittest.TestCase):
    """Test SystemOptimizer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.optimizer = SystemOptimizer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_system_detection(self):
        """Test system detection."""
        self.assertIsInstance(self.optimizer.is_windows, bool)
        self.assertIsInstance(self.optimizer.is_wsl, bool)
    
    def test_package_manager_detection(self):
        """Test package manager detection."""
        result = self.optimizer.verificar_gerenciador_pacotes()
        self.assertIsInstance(result, bool)
    
    def test_resource_measurement(self):
        """Test resource measurement."""
        cpu, memory, disk = self.optimizer.medir_uso_recursos()
        
        self.assertIsInstance(cpu, (int, float))
        self.assertIsInstance(memory, (int, float))
        self.assertIsInstance(disk, (int, float))
        
        self.assertGreaterEqual(cpu, 0)
        self.assertGreaterEqual(memory, 0)
        self.assertGreaterEqual(disk, 0)
        
        self.assertLessEqual(cpu, 100)
        self.assertLessEqual(memory, 100)
        self.assertLessEqual(disk, 100)
    
    def test_memory_analysis(self):
        """Test memory analysis."""
        analysis = self.optimizer.analisar_uso_memoria_detalhado()
        
        self.assertIsInstance(analysis, dict)
        if analysis:  # Only test if analysis succeeded
            self.assertIn('memoria_total_gb', analysis)
            self.assertIn('percentual_uso', analysis)
    
    def test_startup_analysis(self):
        """Test startup analysis."""
        analysis = self.optimizer.analisar_programas_inicializacao()
        
        self.assertIsInstance(analysis, dict)
        if analysis:  # Only test if analysis succeeded
            self.assertIn('total', analysis)
            self.assertIn('classificacao', analysis)
    
    def test_disk_analysis(self):
        """Test disk analysis."""
        analysis = self.optimizer.analisar_uso_disco_detalhado()
        
        self.assertIsInstance(analysis, dict)
        if analysis:  # Only test if analysis succeeded
            self.assertIn('espaco_total_gb', analysis)
            self.assertIn('percentual_uso', analysis)
    
    def test_boot_time_measurement(self):
        """Test boot time measurement."""
        boot_info = self.optimizer.medir_tempo_boot()
        
        self.assertIsInstance(boot_info, dict)
        if boot_info:  # Only test if measurement succeeded
            self.assertIn('boot_timestamp', boot_info)
            self.assertIn('tempo_desde_boot_formatado', boot_info)


class TestSystemMetrics(unittest.TestCase):
    """Test SystemMetrics class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.metrics = SystemMetrics(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_metrics_collection(self):
        """Test metrics collection."""
        metrics = self.metrics.collect_current_metrics()
        
        self.assertIsInstance(metrics, dict)
        if metrics:  # Only test if collection succeeded
            self.assertIn('timestamp', metrics)
            self.assertIn('cpu', metrics)
            self.assertIn('memory', metrics)
            self.assertIn('disk', metrics)
    
    def test_metrics_history(self):
        """Test metrics history management."""
        # Add some test metrics
        test_metrics = {
            'timestamp': '2025-01-01T00:00:00',
            'cpu': {'percent': 50},
            'memory': {'percent': 60},
            'disk': {'percent': 70}
        }
        
        self.metrics.add_metrics_to_history(test_metrics)
        self.assertEqual(len(self.metrics.history_data), 1)
        
        # Test range retrieval
        range_metrics = self.metrics.get_metrics_in_range(24)
        self.assertIsInstance(range_metrics, list)
    
    def test_performance_report(self):
        """Test performance report generation."""
        # Add some test data first
        for i in range(5):
            test_metrics = {
                'timestamp': f'2025-01-01T0{i}:00:00',
                'cpu': {'percent': 50 + i},
                'memory': {'percent': 60 + i},
                'disk': {'percent': 70 + i}
            }
            self.metrics.add_metrics_to_history(test_metrics)
        
        report = self.metrics.generate_performance_report(24)
        self.assertIsInstance(report, dict)
        
        if 'error' not in report:
            self.assertIn('sample_count', report)
            self.assertIn('stability', report)


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_structure(self):
        """Test configuration structure."""
        self.assertIn('app', CONFIG)
        self.assertIn('gui', CONFIG)
        self.assertIn('optimization', CONFIG)
        self.assertIn('safety', CONFIG)
        self.assertIn('system', CONFIG)
    
    def test_config_values(self):
        """Test configuration values."""
        self.assertEqual(CONFIG['app']['version'], '2.0.0')
        self.assertIsInstance(CONFIG['system']['is_windows'], bool)
        self.assertIsInstance(CONFIG['gui']['update_interval'], int)


class TestLogger(unittest.TestCase):
    """Test logging functionality."""
    
    def test_logger_creation(self):
        """Test logger creation."""
        logger = get_logger("test")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test")
    
    def test_logging_levels(self):
        """Test different logging levels."""
        logger = get_logger("test_levels")
        
        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")


def run_tests():
    """Run all tests."""
    print("🧪 Running Paguro Boost Test Suite...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSystemOptimizer))
    test_suite.addTest(unittest.makeSuite(TestSystemMetrics))
    test_suite.addTest(unittest.makeSuite(TestConfiguration))
    test_suite.addTest(unittest.makeSuite(TestLogger))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    
    return success


if __name__ == "__main__":
    run_tests()