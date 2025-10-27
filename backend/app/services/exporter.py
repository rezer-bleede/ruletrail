from __future__ import annotations

import json
from pathlib import Path
from typing import Dict
import hashlib

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..core.config import get_settings


def _ensure_storage_path() -> Path:
    settings = get_settings()
    path = Path(settings.storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, payload: Dict) -> str:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return _hash_file(path)


def _write_html(path: Path, payload: Dict) -> str:
    sections = ["<html><head><meta charset='utf-8'><title>RuleTrail Report</title></head><body>"]
    sections.append("<h1>RuleTrail Run Report</h1>")
    sections.append("<pre>" + json.dumps(payload, indent=2) + "</pre>")
    sections.append("</body></html>")
    path.write_text("\n".join(sections), encoding="utf-8")
    return _hash_file(path)


def _write_pdf(path: Path, payload: Dict) -> str:
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    text_object = c.beginText(40, height - 40)
    text_object.setFont("Helvetica", 10)
    text_object.textLine("RuleTrail Run Report")
    for line in json.dumps(payload, indent=2).splitlines():
        text_object.textLine(line[:90])
    c.drawText(text_object)
    c.showPage()
    c.save()
    return _hash_file(path)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        digest.update(handle.read())
    return digest.hexdigest()


def export_run_artifacts(run_payload: Dict) -> Dict[str, Dict[str, str]]:
    storage = _ensure_storage_path()
    run_id = run_payload.get("id", "run")
    json_path = storage / f"{run_id}.json"
    html_path = storage / f"{run_id}.html"
    pdf_path = storage / f"{run_id}.pdf"

    json_hash = _write_json(json_path, run_payload)
    html_hash = _write_html(html_path, run_payload)
    pdf_hash = _write_pdf(pdf_path, run_payload)

    return {
        "json": {"path": str(json_path), "sha256": json_hash},
        "html": {"path": str(html_path), "sha256": html_hash},
        "pdf": {"path": str(pdf_path), "sha256": pdf_hash},
    }
