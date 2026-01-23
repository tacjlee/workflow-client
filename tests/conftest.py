"""
Pytest configuration for workflow-client tests.
"""

import pytest
import os

# Set default test environment
os.environ.setdefault("DATASTORE_SERVICE_URL", "http://localhost:8010")


@pytest.fixture
def datastore_url():
    """Get datastore service URL from environment."""
    return os.environ.get("DATASTORE_SERVICE_URL", "http://localhost:8010")
