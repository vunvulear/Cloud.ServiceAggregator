"""
AWS CloudFormation Parser

Parses CloudFormation templates (JSON/YAML) and extracts AWS resources.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

try:
    import yaml  # Optional; will use a simple YAML loader if available
except Exception:
    yaml = None

from ..base import BaseIaCParser

AWS_CF_TYPES_KEY = "Type"
AWS_CF_RESOURCES_KEY = "Resources"

class CloudFormationParser(BaseIaCParser):
    """Parses CloudFormation templates and extracts AWS resource information"""

    def parse_files(self, cf_dir: str) -> Dict[str, Dict]:
        cf_path = Path(cf_dir)
        if not cf_path.exists():
            raise FileNotFoundError(f"CloudFormation directory not found: {cf_dir}")

        files = []
        files.extend(cf_path.glob('**/*.json'))
        files.extend(cf_path.glob('**/*.yaml'))
        files.extend(cf_path.glob('**/*.yml'))

        if not files:
            raise FileNotFoundError(f"No CloudFormation templates found in {cf_dir}")

        print(f"Found {len(files)} CloudFormation template(s)")
        for f in files:
            self._parse_file(f)
        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        try:
            content = file_path.read_text(encoding='utf-8')
            data: Dict[str, Any] | None = None
            suffix = file_path.suffix.lower()
            if suffix == '.json':
                data = json.loads(content)
            elif suffix in ('.yaml', '.yml'):
                if yaml:
                    data = yaml.safe_load(content)
                else:
                    data = self._parse_yaml_minimal(content)
            else:
                # attempt JSON first then minimal YAML
                try:
                    data = json.loads(content)
                except Exception:
                    data = self._parse_yaml_minimal(content)

            self._extract_resources(data or {})
            self.parsed_files.append(str(file_path))
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _parse_yaml_minimal(self, content: str) -> Dict[str, Any]:
        """Very small YAML parser for Resources/Type without external deps.
        Supports structures like:
        Resources:
          Name:
            Type: AWS::Service::Resource
        """
        lines = content.splitlines()
        resources: Dict[str, Dict[str, Any]] = {}
        in_resources = False
        current_name: str | None = None
        for line in lines:
            if not in_resources:
                if re.match(r'^\s*Resources\s*:\s*$', line):
                    in_resources = True
                continue
            # Detect new resource name at 2-space indent or more
            m_name = re.match(r'^(\s{2,})([A-Za-z0-9_-]+)\s*:\s*$', line)
            if m_name:
                current_name = m_name.group(2)
                if current_name not in resources:
                    resources[current_name] = {}
                continue
            # Detect Type line under a resource
            if current_name:
                m_type = re.match(r'^\s{4,}Type\s*:\s*(\S+)\s*$', line)
                if m_type:
                    resources[current_name]['Type'] = m_type.group(1)
                    continue
            # Stop if we reach top-level key
            if re.match(r'^\S', line) and in_resources:
                break
        return {AWS_CF_RESOURCES_KEY: resources}

    def _extract_resources(self, template: Dict[str, Any]) -> None:
        if not isinstance(template, dict):
            return
        resources = template.get(AWS_CF_RESOURCES_KEY, {})
        if not isinstance(resources, dict):
            return
        for _, res in resources.items():
            if not isinstance(res, dict):
                continue
            res_type = res.get(AWS_CF_TYPES_KEY, '')
            if isinstance(res_type, str) and res_type.startswith('AWS::'):
                tf_like = self._map_cf_type_to_key(res_type)
                self.resources[tf_like].append(res_type)

    def _map_cf_type_to_key(self, cf_type: str) -> str:
        # Examples: AWS::EC2::Instance -> aws_instance
        parts = cf_type.split('::')
        if len(parts) == 3:
            service, resource = parts[1], parts[2]
            return f"aws_{service.lower()}_{self._to_snake(resource)}"
        return cf_type

    def _to_snake(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_file_extensions(self) -> List[str]:
        return ['.json', '.yaml', '.yml']
