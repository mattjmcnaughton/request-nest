"""Performance tests for ingest endpoint latency.

These tests are excluded from normal CI runs and are intended for local
verification of performance targets. Run with: just perf-test
"""

import statistics
import time

import pytest
from httpx import AsyncClient


@pytest.mark.perf
class TestIngestLatency:
    """Performance tests for ingest endpoint."""

    @pytest.mark.asyncio
    async def test_ingest_p50_latency_under_50ms(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """P50 latency for ingest should be under 50ms on local network.

        This test creates a bin and sends 100 requests, measuring the
        response time for each. The P50 (median) should be under 50ms.

        Note: This test is marked with @pytest.mark.perf and excluded from
        normal CI runs due to environment variability.
        """
        # Create a bin for testing
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Perf Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        # Warmup: send a few requests to warm up connections, caches, etc.
        warmup_count = 5
        for _ in range(warmup_count):
            await client.post(f"/b/{bin_id}/warmup", json={"warmup": True})

        # Measurement: send 100 requests and measure response times
        latencies_ms: list[float] = []
        num_requests = 100

        for i in range(num_requests):
            start = time.perf_counter()
            response = await client.post(
                f"/b/{bin_id}/perf/{i}",
                json={"iteration": i, "timestamp": time.time()},
            )
            end = time.perf_counter()

            assert response.status_code == 200, f"Request {i} failed: {response.text}"

            latency_ms = (end - start) * 1000
            latencies_ms.append(latency_ms)

        # Calculate P50 (median)
        p50 = statistics.median(latencies_ms)
        p95 = sorted(latencies_ms)[int(num_requests * 0.95)]
        p99 = sorted(latencies_ms)[int(num_requests * 0.99)]
        mean = statistics.mean(latencies_ms)

        # Print statistics for debugging
        print(f"\nIngest latency statistics (n={num_requests}):")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        print(f"  Mean: {mean:.2f}ms")
        print(f"  Min: {min(latencies_ms):.2f}ms")
        print(f"  Max: {max(latencies_ms):.2f}ms")

        # Assert P50 < 50ms
        assert p50 < 50, f"P50 latency {p50:.2f}ms exceeds target of 50ms"
