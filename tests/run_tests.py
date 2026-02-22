#!/usr/bin/env python3
"""Test runner for AgentLang test suite."""

import unittest
import sys
import os

# Add parent directory to path so we can import agentlang
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Discover and run all tests
loader = unittest.TestLoader()
start_dir = os.path.dirname(__file__)
suite = loader.discover(start_dir, pattern='test_*.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with error code if tests failed
sys.exit(0 if result.wasSuccessful() else 1)
