# RuleTrail MVP

RuleTrail is an offline-friendly rule explainability and execution engine that ingests Excel rulepacks, evaluates Elasticsearch
records, and produces human-readable decision traces aligned with ADAA & UAEAA requirements. The MVP pairs a FastAPI backend with a
React + Tailwind UI styled using the Presight.ai theme.

## Project structure

```
backend/      FastAPI service, SQLAlchemy models, Excel importer, evaluation engine, tests
frontend/     Vite + React UI with Tailwind styling and vitest unit tests
docker-compose.yml  Orchestrates Elasticsearch, backend, and frontend services
```

Key data assets live in `backend/data/`:

- `seed_rulepack.xlsx` – sample HR & Finance rulepack sheets.
- `datasets.json` – starter Elasticsearch dataset configurations.
- `es_seed.json` – anonymised documents ingested into Elasticsearch on startup.

## Prerequisites

- Python 3.12
- Node.js 20+
- npm 10+
- (Optional) Docker 24+ for containerised runs

## Backend quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8100/api`. Swagger docs live at `http://localhost:8100/docs`. Import failures now return
`400` responses that pinpoint the sheet and row that caused the error so the frontend can surface actionable feedback instead of
generic CORS failures.

### Backend tests

Run pytest from the repository root:

```bash
pytest backend/tests
```

This covers Excel import mapping, rule evaluation, and API CRUD/e2e paths.

### Condition syntax reference

Rule clauses imported from Excel now support three complementary formats:

- **Explicit comparisons** such as `amount > 10` or `status == 'OPEN'`.
- **Inline boolean chains** using `AND`/`OR` connectors on a single line (`amount > 10 AND status == 'OPEN'`).
- **Field presence checks** where a bare field name (`Condition1 and Condition2`) is translated into an "exists" clause that validates whether the corresponding field has a non-empty value. Prefixing the field with `NOT` flips the expectation.

These additions ensure legacy spreadsheets that describe conditions as bullet lists (instead of full comparisons) import successfully while keeping evaluation semantics consistent.

## Frontend quick start

```bash
cd frontend
npm install
npm run dev
```

The UI is served at `http://localhost:5173`. It features navigation across Dashboard, Runs, Rules, Datasets, Start Evaluation,
Results drill-down, and Settings. API calls default to the browser origin (`/api`), so the Vite dev server proxies them to the
backend on `http://localhost:8100` automatically. Override the proxy target by exporting `VITE_DEV_BACKEND_URL` before running
`npm run dev`. For production builds you can still provide a fixed URL via `VITE_API_URL`; otherwise the deployed bundle reuses
its current origin. The nginx image used in Docker Compose already forwards `/api` to the backend container, so no additional
configuration is required when running the stack locally.

### Frontend tests

```bash
cd frontend
npm run test -- --run
```

Vitest validates rule table rendering, rule creation validation, and hook interactions.

### Demo data seeding

Populate Elasticsearch with the bundled demo documents directly from the CLI:

```bash
cd backend
python -m app.scripts.populate_demo
```

The command connects to the configured Elasticsearch hosts and reports how many documents were indexed. The same seed can be
triggered from the UI via the **Load demo data** action on the Datasets screen.

## Dockerised workflow

The MVP ships with a docker compose stack that provisions Elasticsearch, seeds sample indices, and boots the backend/frontend
services.

```bash
docker compose build
docker compose up
```

Elasticsearch publishes to host port `19200` (instead of the default `9200`) to avoid clashes with an existing local
installation. The backend still reaches it internally on port `9200` via the `elasticsearch` service name.

Services:

- **elasticsearch** – single-node cluster with seeded demo documents exposed on `http://localhost:19200` for local access.
- **backend** – FastAPI app exposed on `http://localhost:8100`.
- **frontend** – static React build via nginx on `http://localhost:3100`.

On startup the backend imports `seed_rulepack.xlsx`, registers datasets from `datasets.json`, and loads `es_seed.json` into
Elasticsearch (idempotent).

## Configuration

Runtime options are controlled through environment variables or `backend/.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./ruletrail.db` |
| `ELASTICSEARCH_HOSTS` | Elasticsearch endpoint(s) as JSON array or comma separated list | `["http://elasticsearch:9200"]` |
| `ELASTICSEARCH_HOST` | Legacy single host override (alias for `ELASTICSEARCH_HOSTS`) | `http://elasticsearch:9200` |
| `SEED_EXCEL_PATH` | Path to initial rulepack | `backend/data/seed_rulepack.xlsx` |
| `SEED_DATASET_PATH` | Path to dataset configs | `backend/data/datasets.json` |
| `SEED_ES_PATH` | Path to seed documents | `backend/data/es_seed.json` |

`ELASTICSEARCH_HOSTS` accepts either a JSON array (e.g. `"[\"http://a:9200\",\"http://b:9200\"]"`) or a comma-separated
string (`"http://a:9200,http://b:9200"`). When unset, blank, or filled with only whitespace the backend automatically falls back
to the default single host without raising a configuration error. The legacy `ELASTICSEARCH_HOST` variable remains supported and
is merged into `ELASTICSEARCH_HOSTS` internally.

All file-based settings are resolved relative to both the repository root and the `backend/` directory so you can run
`uvicorn app.main:app` from either location without breaking demo data seeding.

Exports generated via the Results view are written to `backend/data/exports/`.

## Notable features

- Excel importer honours the provided column schema, including boolean clause parsing and rule ordering.
- Rule management UI mirrors Excel fields with validation, search, and inline editing.
- Excel rulepacks can be uploaded directly from the Rules screen; imports instantly refresh the available packs and surface
  inline status feedback.
- Evaluation engine produces per-record traces with PASS/FAIL/WARN/N/A outcomes and concise rationales.
- Hierarchical results explorer (Domain → Rule → Records → Trace) with breadcrumbs and explainability context.
- Dataset manager stores reusable Elasticsearch index/filter configurations.
- Condensed side navigation and form controls keep the UI compact for faster reviews.
- Comprehensive unit + integration coverage for importer, evaluator, and key UI flows.

## Contributing

1. Fork or create a branch.
2. Run both backend and frontend test suites before committing.
3. Submit a PR with context and screenshots when relevant.

Enjoy exploring the compliance-ready decision trails delivered by RuleTrail.
