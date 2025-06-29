#!/usr/bin/env python3
"""
Script to run all tests
"""

import sys
import subprocess

def run_tests():
    """Run the test suite"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'tests.test_paguro_boost'
        ], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)