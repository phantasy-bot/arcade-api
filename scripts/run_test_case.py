#!/usr/bin/env python3
"""
Utility script to run specific test cases with detailed output.
"""
import argparse
import importlib.util
import sys
from pathlib import Path
import json


def load_test_data(test_data_path: str) -> dict:
    """Load test data from a JSON file."""
    path = Path(test_data_path)
    if not path.exists():
        print(f"Error: Test data file not found: {test_data_path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing test data: {e}")
        sys.exit(1)


def run_test_case(module_name: str, test_name: str, test_data: dict = None):
    """Run a specific test case from a test module."""
    # Import the test module
    test_path = f"tests/test_{module_name}.py"
    spec = importlib.util.spec_from_file_location("test_module", test_path)
    if spec is None:
        print(f"Error: Test module not found: {test_path}")
        sys.exit(1)

    test_module = importlib.util.module_from_spec(spec)
    sys.modules["test_module"] = test_module
    spec.loader.exec_module(test_module)

    # Find the test class
    test_class_name = f"Test{module_name.title().replace('_', '')}"
    test_class = getattr(test_module, test_class_name, None)
    if test_class is None:
        print(f"Error: Test class {test_class_name} not found in {test_path}")
        sys.exit(1)

    # Create a test instance
    test_instance = test_class()
    test_instance.setUp()

    # Run the test method
    test_method = getattr(test_instance, test_name, None)
    if test_method is None:
        print(f"Error: Test method {test_name} not found in {test_class_name}")
        sys.exit(1)

    print(f"Running {test_class_name}.{test_name}...\n")
    try:
        if test_data:
            test_method(test_data)
        else:
            test_method()
        print("\n✅ Test passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Run specific test cases with detailed output"
    )
    parser.add_argument("module", help="Name of the module to test (e.g., tic_tac_toe)")
    parser.add_argument("test", help="Name of the test method to run")
    parser.add_argument("--test-data", help="Path to test data JSON file")

    args = parser.parse_args()

    test_data = None
    if args.test_data:
        test_data = load_test_data(args.test_data)

    run_test_case(args.module, args.test, test_data)


if __name__ == "__main__":
    main()
