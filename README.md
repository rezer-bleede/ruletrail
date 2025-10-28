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

The API is available at `http://localhost:8000/api`. Swagger docs live at `http://localhost:8000/docs`.

### Backend tests

Run pytest from the repository root:

```bash
pytest backend/tests
```

This covers Excel import mapping, rule evaluation, and API CRUD/e2e paths.

## Frontend quick start

```bash
cd frontend
npm install
npm run dev
```

The UI is served at `http://localhost:5173`. It features navigation across Dashboard, Runs, Rules, Datasets, Start Evaluation,
Results drill-down, and Settings.

### Frontend tests

```bash
cd frontend
npm run test -- --run
```

Vitest validates rule table rendering, rule creation validation, and hook interactions.

## Dockerised workflow

The MVP ships with a docker compose stack that provisions Elasticsearch, seeds sample indices, and boots the backend/frontend
services.

```bash
docker compose build
docker compose up
```

Services:

- **elasticsearch** – single-node cluster with seeded demo documents.
- **backend** – FastAPI app exposed on `http://localhost:8000`.
- **frontend** – static React build via nginx on `http://localhost:3000`.

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

Exports generated via the Results view are written to `backend/data/exports/`.

## Notable features

- Excel importer honours the provided column schema, including boolean clause parsing and rule ordering.
- Rule management UI mirrors Excel fields with validation, search, and inline editing.
- Evaluation engine produces per-record traces with PASS/FAIL/WARN/N/A outcomes and concise rationales.
- Hierarchical results explorer (Domain → Rule → Records → Trace) with breadcrumbs and explainability context.
- Dataset manager stores reusable Elasticsearch index/filter configurations.
- Comprehensive unit + integration coverage for importer, evaluator, and key UI flows.

## Contributing

1. Fork or create a branch.
2. Run both backend and frontend test suites before committing.
3. Submit a PR with context and screenshots when relevant.

Enjoy exploring the compliance-ready decision trails delivered by RuleTrail.
