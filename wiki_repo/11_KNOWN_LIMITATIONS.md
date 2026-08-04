# Known Limitations

This document lists the operational constraints, mock assumptions, and boundary limitations in the DocSphere MVP release.

---

## 1. Local Fallback Database Modes
* **Behavior**: If Neo4j or Qdrant endpoints are disconnected, the system falls back to in-memory `dict` and `list` indices.
* **Impact**: Data added in fallback mode is transient and will be cleared when the FastAPI gateway process restarts. Ensure that connection strings (`NEO4J_URI`, `QDRANT_HOST`) are correctly configured in production.

---

## 2. In-Memory Background Queues
* **Behavior**: If Redis is not running or the Celery worker connection times out, background tasks fall back to local `asyncio.create_task` executions.
* **Impact**: Jobs executed in fallback mode run inside the main FastAPI process thread. High-concurrency or high-payload PDF parsing jobs could degrade API gateway responsiveness.

---

## 3. Web Crawler Boundaries
* **Behavior**: In the current MVP, the `WebCrawler` returns simulated mock HTML templates and sitemap XML strings.
* **Impact**: Ingestion of live external URL sites requires swapping the mock HTML generator in `web_crawler.py` with standard `aiohttp` / `BeautifulSoup` HTTP requests.

---

## 4. API Rate Limiting
* **Behavior**: The rate limiter checks keys against usage counters stored inside python memory.
* **Impact**: In multi-instance API gateway deployments, rate limits are not shared across pods, which can allow higher usage than configured. Integrating a shared Redis sliding-window check is recommended in production.

---

## 5. Traversal Depth Limits
* **Behavior**: Graph queries (like dependency calculations) enforce a maximum traversal depth of 3 levels.
* **Impact**: Requirements with extremely deep dependency chains beyond 3 levels will not be fully traversed.
