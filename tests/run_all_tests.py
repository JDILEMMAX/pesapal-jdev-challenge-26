#!/usr/bin/env python
"""
Main test runner that executes all test suites in the tests/ directory.
This script provides a centralized entry point for running all tests.
"""
import os
import sys
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# List of test modules to run (in order)
TEST_MODULES = [
    "unit/test_milestones.py",  # Comprehensive milestone tests (consolidated)
    "unit/test_m1_storage.py",   # Storage engine tests
    "unit/test_m1_storage_v2.py",  # Storage engine v2
    "unit/test_m2_sql_pipeline.py",  # SQL pipeline tests
    "unit/test_m3_indexing.py",    # Indexing tests
    "unit/test_m4_transactions.py",  # Transaction tests
]

def run_test(test_file):
    """Run a single test file and return True if successful."""
    test_path = os.path.join(PROJECT_ROOT, test_file)
    
    if not os.path.exists(test_path):
        print(f"⚠ Test file not found: {test_path}")
        return None
    
    print(f"\n{'='*80}")
    print(f"Running: {test_file}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=PROJECT_ROOT,
            capture_output=False,
            timeout=60
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"✗ Test timeout: {test_file}")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False


def main():
    """Run all test suites."""
    print("="*80)
    print("STARTING COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    results = {}
    for test_module in TEST_MODULES:
        result = run_test(test_module)
        results[test_module] = result
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for test_module, result in results.items():
        status = "[PASS]" if result is True else "[FAIL]" if result is False else "[SKIP]"
        print(f"{status}: {test_module}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"{'='*80}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
