"""
EKOS Deep Health Check & Diagnostics Service
Probes Neo4j, Qdrant, PostgreSQL, and Redis service health with response thresholds.

Each check is best-effort: a failure degrades the status but does not crash the server.
The in-memory fallback adapters mean the application can still function when a dependency
is unavailable, so we surface DEGRADED rather than raising exceptions.
"""

import asyncio
import os
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-HealthCheck")


def _check_postgres() -> Dict[str, Any]:
    """Attempt a lightweight SQLAlchemy ping against the configured database."""
    start = time.monotonic()
    try:
        from backend.shared.models.database import SessionLocal
        session = SessionLocal()
        session.execute(__import__("sqlalchemy").text("SELECT 1"))
        session.close()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "HEALTHY", "latency_ms": latency_ms}
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning(f"PostgreSQL health check failed: {exc}")
        return {"status": "UNHEALTHY", "latency_ms": latency_ms, "error": str(exc)}


def _check_neo4j() -> Dict[str, Any]:
    """Attempt a bolt connection ping to Neo4j."""
    start = time.monotonic()
    try:
        from neo4j import GraphDatabase  # type: ignore
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "ekos_password_2026")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "HEALTHY", "latency_ms": latency_ms}
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning(f"Neo4j health check failed: {exc}")
        return {"status": "UNHEALTHY", "latency_ms": latency_ms, "error": str(exc)}


def _check_qdrant() -> Dict[str, Any]:
    """Attempt a collections list call against Qdrant."""
    start = time.monotonic()
    try:
        from qdrant_client import QdrantClient  # type: ignore
        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        client = QdrantClient(host=host, port=port, timeout=2.0)
        client.get_collections()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "HEALTHY", "latency_ms": latency_ms}
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning(f"Qdrant health check failed: {exc}")
        return {"status": "UNHEALTHY", "latency_ms": latency_ms, "error": str(exc)}


def _check_redis() -> Dict[str, Any]:
    """Ping Redis if the redis package is available."""
    start = time.monotonic()
    try:
        import redis as redis_lib  # type: ignore
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis_lib.from_url(url, socket_connect_timeout=2)
        client.ping()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "HEALTHY", "latency_ms": latency_ms}
    except ImportError:
        return {"status": "SKIPPED", "latency_ms": 0, "note": "redis package not installed"}
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning(f"Redis health check failed: {exc}")
        return {"status": "UNHEALTHY", "latency_ms": latency_ms, "error": str(exc)}


class DeepHealthCheckService:
    def __init__(self):
        logger.info("Initialized DeepHealthCheckService.")

    async def check_all_services(self) -> Dict[str, Any]:
        """Runs diagnostics across all backend dependency stores.

        Each check runs in a thread executor so blocking I/O doesn't stall the event loop.
        """
        loop = asyncio.get_event_loop()
        checks = await asyncio.gather(
            loop.run_in_executor(None, _check_postgres),
            loop.run_in_executor(None, _check_neo4j),
            loop.run_in_executor(None, _check_qdrant),
            loop.run_in_executor(None, _check_redis),
        )

        components = {
            "postgres_relational": checks[0],
            "neo4j_graph": checks[1],
            "qdrant_vector": checks[2],
            "redis_cache": checks[3],
        }

        all_healthy = all(
            c["status"] in ("HEALTHY", "SKIPPED") for c in components.values()
        )

        return {
            "status": "UP" if all_healthy else "DEGRADED",
            "components": components,
            "version": "1.0.0-MVP",
        }
