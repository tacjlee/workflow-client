"""
Celery Client Configuration.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CeleryClientConfig:
    """
    Configuration for CeleryClient.

    Reads from environment variables if not explicitly provided.

    Environment Variables:
        CELERY_BROKER_URL: Redis broker URL (default: redis://localhost:6379/0)
        CELERY_RESULT_BACKEND: Redis result backend (default: redis://localhost:6379/0)

    Example:
        # Use defaults from environment
        config = CeleryClientConfig()

        # Override specific settings
        config = CeleryClientConfig(
            broker_url="redis://custom-redis:6379/1",
            default_timeout=60
        )
    """

    broker_url: Optional[str] = None
    result_backend: Optional[str] = None
    default_timeout: int = 300
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = field(default_factory=lambda: ["json"])
    task_track_started: bool = True
    result_expires: int = 3600

    def __post_init__(self):
        """Resolve environment variables after initialization."""
        if self.broker_url is None:
            self.broker_url = os.getenv(
                "CELERY_BROKER_URL", "redis://localhost:6379/0"
            )
        if self.result_backend is None:
            self.result_backend = os.getenv(
                "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
            )
