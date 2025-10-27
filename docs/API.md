# RuleTrail API Overview

## Health & Diagnostics
- `GET /health/ready` – readiness probe returning service status and environment.
- `GET /health/live` – liveness probe.

## Settings & Configuration
- `GET /settings/config` – returns environment configuration (app name, ES index, AI-assist flag).
- `GET /settings/elasticsearch?index=<name>` – checks Elasticsearch connectivity for the requested index.

## Rulepack Registry
- `GET /rulepacks/?tenant_id=<uuid>` – list rulepacks (including versions and rules) for a tenant.
- `POST /rulepacks/import` – multipart upload of Excel rulepack. Query params: `tenant_id`, `name`, `description`.
- `POST /rulepacks/{version_id}/publish` – mark a rulepack version as published.
- `GET /rulepacks/diff?base_id=<uuid>&compare_id=<uuid>` – diff two versions.
- `POST /rulepacks/{version_id}/rules` – create rule within version (mirrors Excel fields).
- `PUT /rulepacks/rules/{rule_id}` – update rule fields.
- `DELETE /rulepacks/rules/{rule_id}` – delete rule.
- `POST /rulepacks/{version_id}/rules/bulk` – bulk operations (`enable`, `disable`, `set_severity`, `set_threshold`).
- `GET /rulepacks/{version_id}/export` – export version to Excel & YAML with file hashes.

## Evaluation Runs
- `POST /runs/` – start evaluation (payload: version id, ES index, filters, created_by).
- `GET /runs/{run_id}` – retrieve run results with hierarchical traces.
- `POST /runs/{run_id}/export` – generate HTML/PDF/JSON artifacts with SHA-256 hashes.

## Audit
- `GET /audit/` – fetch latest audit entries (actor, action, target, metadata).
