from pathlib import Path

import pandas as pd

from app.services.excel_importer import ExcelImportError, load_excel_rulepack


def test_load_excel_rulepack(tmp_path):
    data = {
        'Domain': ['AML'],
        'Group': ['Risk'],
        'Rule ID': ['AML-1'],
        'Severity': ['High'],
        'Message': ['Test message'],
        'Condition:customer_risk': ['high'],
    }
    path = tmp_path / 'rules.xlsx'
    pd.DataFrame(data).to_excel(path, index=False)

    version, checksum, metadata = load_excel_rulepack(path)

    assert version.rules[0].rule_id == 'AML-1'
    assert 'imported_at' in metadata
    assert len(checksum) == 64


def test_missing_condition_raises(tmp_path):
    data = {
        'Domain': ['AML'],
        'Group': ['Risk'],
        'Rule ID': ['AML-1'],
        'Severity': ['High'],
        'Message': ['Test message'],
    }
    path = tmp_path / 'rules.xlsx'
    pd.DataFrame(data).to_excel(path, index=False)

    try:
        load_excel_rulepack(path)
    except ExcelImportError as exc:
        assert "missing condition" in str(exc)
    else:
        raise AssertionError('expected ExcelImportError')
