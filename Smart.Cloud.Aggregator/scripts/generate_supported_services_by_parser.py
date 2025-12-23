#!/usr/bin/env python3
"""
Generate a markdown file listing, grouped by cloud vendor (Azure, AWS),
for each parser the services that the project can map (based on SERVICE_MAPPING).

Output: docs/SUPPORTED_SERVICES_BY_PARSER.md
"""
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

import sys
# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.service_mapping import SERVICE_MAPPING  # type: ignore

# Vendor -> { Parser Name -> selector }
VENDOR_PARSERS = {
    'Azure': {
        'Terraform (Azure)': lambda k: k.startswith('azurerm_'),
        'Bicep': lambda k: k.startswith('Microsoft.'),
        'ARM Template': lambda k: k.startswith('Microsoft.'),
        'PowerShell': lambda k: k.startswith('Microsoft.'),
        'Azure CLI': lambda k: k.startswith('Microsoft.'),
    },
    'AWS': {
        'Terraform (AWS)': lambda k: k.startswith('aws_'),
        'CloudFormation': lambda k: k.startswith('aws_'),
        'Python (AWS SDK)': lambda k: k.startswith('aws_'),
        'Bash (AWS CLI)': lambda k: k.startswith('aws_'),
        'TypeScript (AWS)': lambda k: k.startswith('aws_'),
        'Go (AWS)': lambda k: k.startswith('aws_'),
        'Java/C# (AWS)': lambda k: k.startswith('aws_'),
    },
}


def build_services_for_keys(keys: List[str]) -> Dict[str, List[str]]:
    grouped: Dict[str, set] = defaultdict(set)
    for k in keys:
        category, service = SERVICE_MAPPING[k]
        grouped[category].add(service)
    # convert to sorted lists
    return {cat: sorted(svcs) for cat, svcs in sorted(grouped.items(), key=lambda x: x[0])}


def _compute_vendor_summary() -> Dict[str, List[Tuple[str, int, int]]]:
    summary: Dict[str, List[Tuple[str, int, int]]] = {}
    for vendor, parsers in VENDOR_PARSERS.items():
        rows: List[Tuple[str, int, int]] = []
        for parser_name, selector in parsers.items():
            keys = [k for k in SERVICE_MAPPING.keys() if selector(k)]
            if not keys:
                continue
            services_by_cat = build_services_for_keys(keys)
            total_services = sum(len(v) for v in services_by_cat.values())
            rows.append((parser_name, total_services, len(services_by_cat)))
        summary[vendor] = rows
    return summary


def generate_md() -> str:
    lines: List[str] = []
    lines.append('# Supported Services by Parser')
    lines.append('')
    lines.append('This document lists, grouped by cloud vendor, the services that are mapped by each parser. The list is derived from `src/service_mapping.py`.')
    lines.append('')

    # Top summary section
    lines.append('## Summary')
    lines.append('')
    vendor_summary = _compute_vendor_summary()
    for vendor, rows in vendor_summary.items():
        lines.append(f'### {vendor}')
        for parser_name, total_services, total_categories in rows:
            lines.append(f'- {parser_name}: {total_services} services across {total_categories} categories')
        lines.append('')

    # Detailed listings per vendor and parser
    for vendor, parsers in VENDOR_PARSERS.items():
        lines.append(f'## {vendor}')
        lines.append('')
        for parser_name, selector in parsers.items():
            keys = [k for k in SERVICE_MAPPING.keys() if selector(k)]
            if not keys:
                continue
            services_by_cat = build_services_for_keys(keys)
            lines.append(f'### {parser_name}')
            lines.append('')
            total_services = sum(len(v) for v in services_by_cat.values())
            lines.append(f'- Total categories: {len(services_by_cat)}')
            lines.append(f'- Total services: {total_services}')
            lines.append('')
            for cat, svcs in services_by_cat.items():
                lines.append(f'#### {cat}')
                for svc in svcs:
                    lines.append(f'- {svc}')
                lines.append('')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main() -> int:
    md = generate_md()
    out_path = ROOT / 'docs' / 'SUPPORTED_SERVICES_BY_PARSER.md'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding='utf-8')
    print(f'Wrote: {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
