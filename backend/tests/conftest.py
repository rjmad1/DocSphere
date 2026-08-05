"""
EKOS Test Configuration
Sets up environment variables required for the auth bypass in all tests,
so each test file does not need to manage them individually.
"""
import os
import pytest


def pytest_configure(config):
    """Set test environment variables before any test collection or execution."""
    os.environ.setdefault("EKOS_BYPASS_AUTH_IN_TESTS", "true")
    os.environ.setdefault("EKOS_MASTER_KEY", "test_master_key_32b_for_unit_tests_")
    os.environ.setdefault("EKOS_JWT_SECRET", "test_jwt_secret_32b_for_unit_tests__")
