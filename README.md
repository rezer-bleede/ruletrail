# RuleTrail MVP

RuleTrail is an offline-friendly rule explainability and execution platform for ADAA & UAEAA compliance teams. Upload Excel rulepacks, execute against Elasticsearch data, and drill into deterministic traces with human-readable narratives.

## Key Features
- **Excel Rulepack Registry** – auto-detect sheets/headers, versioning with checksums, metadata, and diffing.
- **Rule Management UI** – create/edit/delete rules, bulk enable/disable/severity/threshold updates, draft vs publish workflow.
- **Evaluation Engine** – deterministic rule execution with hierarchical evidence down to individual records.
- **Explainability** – per-rule narratives plus full trace exports (HTML/PDF/JSON) with SHA-256 hashes.
- **Results Explorer** – multi-level drilldown (entity → domain → rule → record) with global filters and AI-assist toggle (placeholder).
- **Audit & Governance** – immutable audit log, tenant scoping, RBAC placeholders.
- **Single-command Bring-up** – `docker compose up` starts Postgres, Elasticsearch, backend, frontend, and demo data seeding.

## Repository Layout
```
backend/    FastAPI service, SQLModel persistence, evaluation & export logic
frontend/   Vite + React UI styled with Presight.ai-inspired theme
seed/       Demo Excel rulepack, Elasticsearch sample dataset, seeding utilities
docs/       API overview and coordination notes
```

## Getting Started
1. **Clone & configure**
   ```bash
   cp .env.example .env
   # adjust DATABASE_URL / ELASTICSEARCH_HOSTS / STORAGE_PATH as needed
   ```
2. **Launch the full stack**
   ```bash
   docker compose up --build
   ```
   Services:
   - `backend` FastAPI on `http://localhost:8000`
   - `frontend` UI on `http://localhost:5173`
   - `postgres` persistence for rule registry & audit logs
   - `elasticsearch` single-node demo cluster (seeded by `es-seed`)

3. **Demo workflow**
   - Sign in to UI (no auth yet) → Dashboard shows KPIs & recent activity.
   - Import `seed/sample_rulepack.xlsx` or upload your own Excel file.
   - Manage rules (enable/disable, bulk edits, add new) before publishing.
   - Configure Elasticsearch index & filters via Run Wizard → start evaluation.
   - Explore results hierarchy, narratives, evidence, and export artifacts.

## Running Tests
```bash
# backend unit + integration tests
cd backend
pytest -q

# frontend type & build checks
cd ../frontend
npm install
npm run build
```
Latest CI-equivalent runs (captured during development):
- Pytest: see `deb530†L1-L38`
- Frontend build: see `83ff92†L1-L20`

## Manual Testing Checklist
- [x] Import Excel rulepack → version visible with checksum & metadata
- [x] Create/edit/delete rules, bulk severity/threshold updates, publish workflow
- [x] Run evaluation against Elasticsearch demo index → inspect multi-level drilldown
- [x] Export HTML/PDF/JSON artifacts → hashes displayed
- [x] Audit log captures imports, rule edits, runs, exports

## Configuration Reference
Environment variables (see `.env.example`):
- `DATABASE_URL` – SQLModel connection string (defaults to Postgres in compose)
- `ELASTICSEARCH_HOSTS` – comma-separated hosts (default `http://elasticsearch:9200`)
- `ELASTICSEARCH_INDEX` – default demo index (`ruletrail-demo`)
- `STORAGE_PATH` – location for exports/uploads (mounted volume in docker)
- `FEATURE_AI_ASSIST_ENABLED` – toggles optional narrative enhancer (UI placeholder)

## API Contracts
See [docs/API.md](docs/API.md) for endpoint inventory covering rulepacks, runs, exports, settings, and audit logging.

## Notes & Next Steps
- Replace demo RBAC and tenant stubs with production auth.
- Move to timezone-aware timestamps (`datetime.now(datetime.UTC)`) in a future iteration.
- Harden Elasticsearch integration (query templating, pagination, security) before production.
