"""
Unit tests for Quality Gates Engine (src/quality_gates.py).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from quality_gates import run_quality_gates


def test_quality_gates_execution():
    passed, results, stats = run_quality_gates()
    assert passed is True, f"Quality gates failed: {results}"
    assert stats["passed_gates"] == len(results)
    print("[PASS] all quality gates passed cleanly")


def run():
    test_quality_gates_execution()
    return 0


if __name__ == "__main__":
    exit(run())
