#!/usr/bin/env python3
"""
Test runner for the game arcade API.

This script discovers and runs all tests in the tests directory.
"""
import unittest
import sys


def run_tests():
    """Run all tests in the tests directory."""
    # Discover and run all tests in the tests directory
    test_suite = unittest.defaultTestLoader.discover("tests")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    run_tests()
