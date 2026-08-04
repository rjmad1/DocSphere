# Project Memory

This document stores the historical context, developer conventions, lessons learned, and resolved issues in the DocSphere project.

---

## 1. Resolved Technical Issues & AI Lessons Learned

### Mocking Context Managers in Python Tests
* **Issue**: In `neo4j_adapter.py`, the session is entered using a context manager: `with self.driver.session() as session:`. 
* **Lesson**: When mocking context managers in python, `mock_driver.session.return_value = mock_session` is insufficient. The `__enter__` method of the mock is what returns the active context. Therefore, mock methods (like `execute_write` and `execute_read`) must be configured on `mock_session.__enter__.return_value`. Configuring them directly on `mock_session` causes the calls inside the context block to bypass side-effects and fail.

### Vite Entry Point Resolution on Windows
* **Issue**: Vite requires an `index.html` file in the project folder to auto-determine entry points.
* **Lesson**: Running Vite dev servers on custom workspace paths requires configuring a local `index.html` referencing `/src/main.tsx` inside the `frontend/` directory, and launching Vite with `--port 3000` to prevent port collisions.

### Node.js Monorepo Module Resolution
* **Issue**: Playwright config files located at the root of a project cannot resolve packages installed under subfolders like `frontend/node_modules` unless a root-level `package.json` declares the devDependencies.
* **Lesson**: Declare core testing utilities (`@playwright/test`, `typescript`) at the workspace root `package.json` to allow root-level script execution.

---

## 2. Developer Conventions & Rules
* **No Speculative Abstractions (YAGNI)**: Code must be minimal. No placeholder parameters or abstract structures for hypothetical requirements.
* **Robust Fallbacks**: Always write local fallback dictionary/list implementations for database and queue adapters. This guarantees unit test stability during CI/CD.
* **Typing Rigor**: Avoid the `any` type in TypeScript. Use standard primitives (`string`, `number`, `boolean`) over invalid types (`str`).

---

## 3. Successful Design Patterns
* **Adapter Pattern**: Wrapping Neo4j and Qdrant drivers in production adapters that present a clean interface to the service layer.
* **ABC adapters**: Using abstract base classes (like `BaseChannelAdapter`) to unify event processing, signature verification, and response sending across platforms.
