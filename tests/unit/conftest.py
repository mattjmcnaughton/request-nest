"""Pytest configuration for unit tests.

Unit tests run without database access. This conftest overrides the
session-scoped database setup fixture from the root conftest.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Override root conftest fixture to skip database setup for unit tests."""
    yield
