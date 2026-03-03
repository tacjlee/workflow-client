"""
GraphKnowledgeClient

Synchronous HTTP client for workflow-graph-knowledge service.
Provides access to FalkorDB-backed graph knowledge operations.

Usage:
    from workflow_client import GraphKnowledgeClient

    client = GraphKnowledgeClient()

    # Create viewpoint
    viewpoint = client.create_viewpoint("Must", strategy="TEMPLATE", vp_ids=["VP-001"])

    # Get co-occurrences
    co_occurrences = client.get_co_occurrences("Must")

    # Learn from golden data
    result = client.learn_from_golden(
        screen_id="SC011",
        screen_name="Account Management",
        widgets=[...],
        testcases=[...]
    )

    # Infer missing viewpoints
    suggestions = client.infer_viewpoints("SC011")
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any, Callable
from functools import wraps

import httpx

from .models.graph_knowledge import (
    ViewpointNode,
    ViewpointCreate,
    ViewpointUpdate,
    CoOccurrence,
    SimilarViewpoint,
    TestCaseCreate,
    TestCaseNode,
    TestCaseSimilarity,
    ScreenCreate,
    ScreenNode,
    WidgetCreate,
    WidgetNode,
    CoOccurrenceDiscovery,
    ViewpointSuggestion,
    GoldenWidget,
    GoldenTestCase,
    GoldenLearningResult,
    GraphStats,
)

logger = logging.getLogger(__name__)


class GraphKnowledgeError(Exception):
    """Base exception for graph knowledge client errors."""
    pass


class GraphKnowledgeConnectionError(GraphKnowledgeError):
    """Raised when connection to graph knowledge service fails."""
    pass


class GraphKnowledgeTimeoutError(GraphKnowledgeError):
    """Raised when request to graph knowledge service times out."""
    pass


class GraphKnowledgeAPIError(GraphKnowledgeError):
    """Raised when graph knowledge service returns an error response."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class GraphKnowledgeNotFoundError(GraphKnowledgeError):
    """Raised when requested resource is not found."""
    pass


def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except (GraphKnowledgeConnectionError, GraphKnowledgeTimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class GraphKnowledgeClient:
    """
    Synchronous HTTP client for workflow-graph-knowledge service.

    Features:
    - Connection pooling
    - Retry with exponential backoff
    - Type-safe request/response models
    - Viewpoint, TestCase, Screen, Widget CRUD
    - Learning and recommendation APIs
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        read_timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        interceptors: Optional[List[Callable[[Dict[str, str]], Dict[str, str]]]] = None
    ):
        """
        Initialize GraphKnowledgeClient.

        Args:
            base_url: Service URL (default: from GRAPH_KNOWLEDGE_SERVICE_URL env or http://localhost:8006)
            read_timeout: Read timeout in seconds (default: 30)
            connect_timeout: Connection timeout in seconds (default: 10)
            max_retries: Maximum retry attempts
            interceptors: List of request interceptors
        """
        self._base_url = base_url or os.getenv("GRAPH_KNOWLEDGE_SERVICE_URL", "http://localhost:8006")
        self._timeout = httpx.Timeout(read_timeout, connect=connect_timeout)
        self._max_retries = max_retries
        self._client: Optional[httpx.Client] = None
        self._interceptors: List[Callable[[Dict[str, str]], Dict[str, str]]] = interceptors or []

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=self._base_url,
                timeout=self._timeout
            )
        return self._client

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code in (200, 201):
            return response.json()
        elif response.status_code == 404:
            raise GraphKnowledgeNotFoundError(f"Resource not found: {response.text}")
        elif response.status_code >= 500:
            raise GraphKnowledgeAPIError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text
            )
        else:
            raise GraphKnowledgeAPIError(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text
            )

    def _apply_interceptors(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Apply all registered interceptors to headers."""
        for interceptor in self._interceptors:
            headers = interceptor(headers)
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        try:
            client = self._get_client()

            headers = {"Content-Type": "application/json"}
            headers = self._apply_interceptors(headers)

            response = client.request(
                method=method,
                url=endpoint,
                json=json,
                params=params,
                headers=headers
            )
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise GraphKnowledgeConnectionError(f"Connection failed: {e}")
        except httpx.TimeoutException as e:
            raise GraphKnowledgeTimeoutError(f"Request timed out: {e}")

    def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    def health_check(self) -> Dict[str, Any]:
        """Check graph knowledge service health."""
        try:
            client = self._get_client()
            response = client.get("/health")
            if response.status_code == 200:
                return response.json()
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    # =========================================================================
    # VIEWPOINT OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def create_viewpoint(
        self,
        name: str,
        strategy: str = "TEMPLATE",
        vp_ids: List[str] = None,
        description: Optional[str] = None,
    ) -> ViewpointNode:
        """
        Create or update a viewpoint node.

        Args:
            name: Viewpoint name (e.g., "Must", "Function")
            strategy: Strategy type ("TEMPLATE", "COMBINATORIAL", "TARGETED_LLM")
            vp_ids: List of VP IDs (e.g., ["VP-001", "VP-002"])
            description: Optional description

        Returns:
            ViewpointNode with created/updated viewpoint
        """
        data = self._make_request(
            "POST",
            "/api/v1/viewpoints",
            json={
                "name": name,
                "strategy": strategy,
                "vp_ids": vp_ids or [],
                "description": description,
            }
        )
        return ViewpointNode(**data)

    @retry_with_backoff(max_retries=3)
    def get_viewpoint(self, name: str) -> Optional[ViewpointNode]:
        """
        Get viewpoint by name.

        Args:
            name: Viewpoint name

        Returns:
            ViewpointNode or None if not found
        """
        try:
            data = self._make_request("GET", f"/api/v1/viewpoints/{name}")
            return ViewpointNode(**data)
        except GraphKnowledgeNotFoundError:
            return None

    @retry_with_backoff(max_retries=3)
    def list_viewpoints(self, limit: int = 100, offset: int = 0) -> List[ViewpointNode]:
        """
        List all viewpoints.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of ViewpointNode
        """
        data = self._make_request(
            "GET",
            "/api/v1/viewpoints",
            params={"limit": limit, "offset": offset}
        )
        return [ViewpointNode(**v) for v in data]

    @retry_with_backoff(max_retries=3)
    def get_co_occurrences(
        self,
        viewpoint: str,
        min_frequency: int = 2,
        min_confidence: float = 0.5,
    ) -> List[CoOccurrence]:
        """
        Get viewpoints that co-occur with the given viewpoint.

        Args:
            viewpoint: Viewpoint name
            min_frequency: Minimum co-occurrence frequency
            min_confidence: Minimum confidence score

        Returns:
            List of CoOccurrence relationships
        """
        data = self._make_request(
            "GET",
            f"/api/v1/viewpoints/{viewpoint}/co-occurrences",
            params={
                "min_frequency": min_frequency,
                "min_confidence": min_confidence,
            }
        )
        return [CoOccurrence(**c) for c in data.get("viewpoints", [])]

    @retry_with_backoff(max_retries=3)
    def get_similar_viewpoints(
        self,
        viewpoint: str,
        min_score: float = 0.7,
        limit: int = 10,
    ) -> List[SimilarViewpoint]:
        """
        Get viewpoints similar to the given viewpoint.

        Args:
            viewpoint: Viewpoint name
            min_score: Minimum similarity score
            limit: Maximum number of results

        Returns:
            List of SimilarViewpoint
        """
        data = self._make_request(
            "GET",
            f"/api/v1/viewpoints/{viewpoint}/similar",
            params={
                "min_score": min_score,
                "limit": limit,
            }
        )
        return [SimilarViewpoint(**s) for s in data.get("viewpoints", [])]

    @retry_with_backoff(max_retries=3)
    def delete_viewpoint(self, name: str) -> bool:
        """
        Delete viewpoint and its relationships.

        Args:
            name: Viewpoint name

        Returns:
            True if deleted
        """
        try:
            self._make_request("DELETE", f"/api/v1/viewpoints/{name}")
            return True
        except GraphKnowledgeNotFoundError:
            return False

    # =========================================================================
    # TEST CASE OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def create_testcase(
        self,
        content: str,
        viewpoint: str,
        screen_id: str,
        procedure: str = "",
        expected_result: str = "",
        widget_id: Optional[str] = None,
        mode: Optional[str] = None,
        priority: str = "Medium",
        source_type: str = "golden",
    ) -> TestCaseNode:
        """
        Create a test case node with relationships.

        Args:
            content: Test case content/description
            viewpoint: Viewpoint name this test case tests
            screen_id: Screen ID this test case belongs to
            procedure: Test procedure steps
            expected_result: Expected result
            widget_id: Optional widget ID this test case targets
            mode: Optional mode (LIST, ADD, EDIT)
            priority: Priority (High, Medium, Low)
            source_type: Source type (golden, generated, manual)

        Returns:
            TestCaseNode with created test case
        """
        data = self._make_request(
            "POST",
            "/api/v1/testcases",
            json={
                "content": content,
                "viewpoint": viewpoint,
                "screen_id": screen_id,
                "procedure": procedure,
                "expected_result": expected_result,
                "widget_id": widget_id,
                "mode": mode,
                "priority": priority,
                "source_type": source_type,
            }
        )
        return TestCaseNode(**data)

    @retry_with_backoff(max_retries=3)
    def create_testcases_bulk(self, testcases: List[TestCaseCreate]) -> int:
        """
        Bulk create test cases.

        Args:
            testcases: List of TestCaseCreate models

        Returns:
            Number of created test cases
        """
        data = self._make_request(
            "POST",
            "/api/v1/testcases/bulk",
            json={"items": [tc.model_dump() for tc in testcases]}
        )
        return data.get("created", 0)

    @retry_with_backoff(max_retries=3)
    def get_testcase(self, testcase_id: str) -> Optional[TestCaseNode]:
        """
        Get test case by ID.

        Args:
            testcase_id: Test case ID

        Returns:
            TestCaseNode or None if not found
        """
        try:
            data = self._make_request("GET", f"/api/v1/testcases/{testcase_id}")
            return TestCaseNode(**data)
        except GraphKnowledgeNotFoundError:
            return None

    @retry_with_backoff(max_retries=3)
    def get_similar_testcases(
        self,
        testcase_id: str,
        min_score: float = 0.7,
        cross_screen: bool = True,
        limit: int = 20,
    ) -> List[TestCaseSimilarity]:
        """
        Find similar test cases.

        Args:
            testcase_id: Test case ID
            min_score: Minimum similarity score
            cross_screen: Include test cases from other screens
            limit: Maximum number of results

        Returns:
            List of TestCaseSimilarity
        """
        data = self._make_request(
            "GET",
            f"/api/v1/testcases/{testcase_id}/similar",
            params={
                "min_score": min_score,
                "cross_screen": cross_screen,
                "limit": limit,
            }
        )
        return [TestCaseSimilarity(**tc) for tc in data.get("testcases", [])]

    @retry_with_backoff(max_retries=3)
    def get_testcases_by_screen(self, screen_id: str, limit: int = 100) -> List[TestCaseNode]:
        """
        List test cases for a screen.

        Args:
            screen_id: Screen ID
            limit: Maximum number of results

        Returns:
            List of TestCaseNode
        """
        data = self._make_request(
            "GET",
            f"/api/v1/testcases/by-screen/{screen_id}",
            params={"limit": limit}
        )
        return [TestCaseNode(**tc) for tc in data]

    @retry_with_backoff(max_retries=3)
    def get_testcases_by_viewpoint(self, viewpoint: str, limit: int = 100) -> List[TestCaseNode]:
        """
        List test cases for a viewpoint.

        Args:
            viewpoint: Viewpoint name
            limit: Maximum number of results

        Returns:
            List of TestCaseNode
        """
        data = self._make_request(
            "GET",
            f"/api/v1/testcases/by-viewpoint/{viewpoint}",
            params={"limit": limit}
        )
        return [TestCaseNode(**tc) for tc in data]

    # =========================================================================
    # SCREEN OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def create_screen(
        self,
        screen_id: str,
        name: str,
        document_type: str = "CRUD",
        modes: List[str] = None,
    ) -> ScreenNode:
        """
        Create or update a screen node.

        Args:
            screen_id: Screen ID (e.g., "SC011")
            name: Screen name
            document_type: Document type (CRUD, List, Form)
            modes: List of modes (LIST, ADD, EDIT)

        Returns:
            ScreenNode with created/updated screen
        """
        data = self._make_request(
            "POST",
            "/api/v1/screens",
            json={
                "id": screen_id,
                "name": name,
                "document_type": document_type,
                "modes": modes or ["LIST", "ADD", "EDIT"],
            }
        )
        return ScreenNode(**data)

    @retry_with_backoff(max_retries=3)
    def get_screen(self, screen_id: str) -> Optional[ScreenNode]:
        """
        Get screen with statistics.

        Args:
            screen_id: Screen ID

        Returns:
            ScreenNode or None if not found
        """
        try:
            data = self._make_request("GET", f"/api/v1/screens/{screen_id}")
            return ScreenNode(**data)
        except GraphKnowledgeNotFoundError:
            return None

    @retry_with_backoff(max_retries=3)
    def list_screens(self, limit: int = 100, offset: int = 0) -> List[ScreenNode]:
        """
        List all screens.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of ScreenNode
        """
        data = self._make_request(
            "GET",
            "/api/v1/screens",
            params={"limit": limit, "offset": offset}
        )
        return [ScreenNode(**s) for s in data]

    @retry_with_backoff(max_retries=3)
    def get_similar_screens(
        self,
        screen_id: str,
        min_score: float = 0.7,
        limit: int = 10,
    ) -> List[ScreenNode]:
        """
        Find similar screens.

        Args:
            screen_id: Screen ID
            min_score: Minimum similarity score
            limit: Maximum number of results

        Returns:
            List of ScreenNode
        """
        data = self._make_request(
            "GET",
            f"/api/v1/screens/{screen_id}/similar",
            params={
                "min_score": min_score,
                "limit": limit,
            }
        )
        return [ScreenNode(**s) for s in data]

    # =========================================================================
    # WIDGET OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def create_widget(
        self,
        widget_id: str,
        name: str,
        widget_type: str,
        screen_id: str,
        semantic_type: Optional[str] = None,
    ) -> WidgetNode:
        """
        Create or update a widget node.

        Args:
            widget_id: Widget ID
            name: Widget name
            widget_type: Widget type (BUTTON, TEXT_INPUT, etc.)
            screen_id: Screen ID this widget belongs to
            semantic_type: Optional semantic type

        Returns:
            WidgetNode with created/updated widget
        """
        data = self._make_request(
            "POST",
            "/api/v1/screens/widgets",
            json={
                "id": widget_id,
                "name": name,
                "type": widget_type,
                "screen_id": screen_id,
                "semantic_type": semantic_type,
            }
        )
        return WidgetNode(**data)

    @retry_with_backoff(max_retries=3)
    def get_widgets_by_screen(self, screen_id: str) -> List[WidgetNode]:
        """
        List widgets for a screen.

        Args:
            screen_id: Screen ID

        Returns:
            List of WidgetNode
        """
        data = self._make_request("GET", f"/api/v1/screens/{screen_id}/widgets")
        return [WidgetNode(**w) for w in data]

    # =========================================================================
    # LEARNING OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def discover_co_occurrences(self, screen_id: str) -> List[CoOccurrenceDiscovery]:
        """
        Discover viewpoint co-occurrences for a screen.

        Analyzes test cases to find which viewpoints often appear together.

        Args:
            screen_id: Screen ID to analyze

        Returns:
            List of discovered co-occurrences
        """
        data = self._make_request(
            "POST",
            "/api/v1/learn/co-occurrences",
            json={"screen_id": screen_id}
        )
        return [CoOccurrenceDiscovery(**c) for c in data.get("discovered", [])]

    @retry_with_backoff(max_retries=3)
    def compute_similarities(self, screen_id: str, threshold: float = 0.7) -> int:
        """
        Compute similarities between test cases.

        Args:
            screen_id: Screen ID
            threshold: Similarity threshold

        Returns:
            Number of similarity links created
        """
        data = self._make_request(
            "POST",
            "/api/v1/learn/similarities",
            json={"screen_id": screen_id, "threshold": threshold}
        )
        return data.get("links_created", 0)

    @retry_with_backoff(max_retries=3)
    def infer_viewpoints(
        self,
        screen_id: str,
        widget_ids: List[str] = None,
    ) -> List[ViewpointSuggestion]:
        """
        Suggest missing viewpoints based on graph patterns.

        Uses co-occurrence patterns and similar screens to recommend
        viewpoints that might be missing from the current screen.

        Args:
            screen_id: Screen ID
            widget_ids: Optional list of widget IDs for context

        Returns:
            List of ViewpointSuggestion with confidence scores
        """
        data = self._make_request(
            "POST",
            "/api/v1/learn/infer-viewpoints",
            json={
                "screen_id": screen_id,
                "widget_ids": widget_ids or [],
            }
        )
        return [ViewpointSuggestion(**s) for s in data.get("suggestions", [])]

    @retry_with_backoff(max_retries=3)
    def learn_from_golden(
        self,
        screen_id: str,
        screen_name: str,
        document_type: str = "CRUD",
        modes: List[str] = None,
        widgets: List[GoldenWidget] = None,
        testcases: List[GoldenTestCase] = None,
    ) -> GoldenLearningResult:
        """
        Full learning pipeline from golden data.

        Creates screen, widgets, test cases, viewpoints, and discovers
        co-occurrence patterns in a single operation.

        Args:
            screen_id: Screen ID
            screen_name: Screen name
            document_type: Document type (CRUD, List, Form)
            modes: List of modes
            widgets: List of GoldenWidget
            testcases: List of GoldenTestCase

        Returns:
            GoldenLearningResult with counts of created entities
        """
        data = self._make_request(
            "POST",
            "/api/v1/learn/from-golden",
            json={
                "screen_id": screen_id,
                "screen_name": screen_name,
                "document_type": document_type,
                "modes": modes or ["LIST", "ADD", "EDIT"],
                "widgets": [w.model_dump() for w in (widgets or [])],
                "testcases": [tc.model_dump() for tc in (testcases or [])],
            }
        )
        return GoldenLearningResult(**data)

    @retry_with_backoff(max_retries=3)
    def compute_screen_similarities(self, threshold: float = 0.5) -> int:
        """
        Compute screen similarities based on shared viewpoints.

        Args:
            threshold: Similarity threshold

        Returns:
            Number of similarity links created
        """
        data = self._make_request(
            "POST",
            f"/api/v1/learn/screen-similarity",
            params={"threshold": threshold}
        )
        return data.get("links_created", 0)

    # =========================================================================
    # STATS OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def get_stats(self) -> GraphStats:
        """
        Get graph statistics.

        Returns:
            GraphStats with node and relationship counts
        """
        data = self._make_request("GET", "/api/v1/stats")
        return GraphStats(**data)


# Singleton instance
_graph_knowledge_client: Optional[GraphKnowledgeClient] = None


def get_graph_knowledge_client() -> GraphKnowledgeClient:
    """Get singleton GraphKnowledgeClient instance."""
    global _graph_knowledge_client
    if _graph_knowledge_client is None:
        _graph_knowledge_client = GraphKnowledgeClient()
    return _graph_knowledge_client
