# Automation Catalog

This document catalogues all task automations, crawlers, schedulers, background jobs, and test execution configs in DocSphere.

---

## 1. Web Crawler Automation (`web_crawler.py`)
Responsible for scanning online documentation and indexing it directly into DocSphere.
* **Single Page Crawl**: Fetch text and titles from a single URL.
* **Sitemap Crawl**: Parses a target XML sitemap (e.g. `/sitemap.xml`) to extract Loc URLs and fetch them concurrently.
* **Recursive BFS Crawl**: Breadth-First-Search crawl that follows inline domain relative links up to a configurable max depth (e.g. 3 levels) and max page count (e.g. 50 pages).
* **Automatic Deduping**: Visited loops logic prevents recursive crawlers from scanning duplicate URLs.

---

## 2. Background Queue Workers (`celery_app.py`)
High-latency processing scripts offloaded to separate background workers.
* **`process_document_chunk`**: Parses incoming document uploads, extracts entities, encrypts PII values using CMEK, and updates Neo4j/Qdrant adapters.
* **`compute_change_impact`**: Simulates structural downstream effects when a requirement is altered. Generates severity indicators and validation outputs.

---

## 3. Test Runner Automations
* **Pytest coverage term-missing**:
  ```powershell
  python -m pytest --cov=backend backend/tests/ --cov-report=term-missing
  ```
  Runs the full Python test runner and prints uncovered branches line-by-line.
* **Playwright E2E runners**:
  ```powershell
  npx playwright test --project=chromium
  npx playwright test --project=mobile-chrome
  ```
  Automatically spins up Vite and Uvicorn dev servers, executes chromium or mobile chrome browser projects, verifies WCAG accessibility rules, visual screen compares, and shuts down dev servers cleanly.
