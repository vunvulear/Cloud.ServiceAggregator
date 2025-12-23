"""
Report Generator Module

Generates comprehensive markdown and JSON reports of Azure services.
"""

import json
from typing import Dict
from datetime import datetime


class ReportGenerator:
    """Generates markdown and JSON reports of Azure services"""

    def __init__(self, aggregated_services: Dict[str, Dict], metadata: Dict = None, include_parsed_files: bool = True, include_legacy_header: bool = True):
        """
        Initialize the report generator.
        
        Args:
            aggregated_services: Dictionary of aggregated services
            metadata: Optional metadata about the analysis (e.g., parsed files, parser types)
            include_parsed_files: Whether to include 'parsed_files' in JSON output (default: True)
            include_legacy_header: Whether to include '# Azure Services Assessment Report' in markdown header (default: True)
        """
        self.services = aggregated_services
        self.metadata = metadata or {}
        self.include_parsed_files = include_parsed_files
        self.include_legacy_header = include_legacy_header

    def generate_markdown(self) -> str:
        """
        Generate a comprehensive markdown report.
        
        Returns:
            Markdown formatted report as string
        """
        report = self._header()
        report += self._metadata_section()
        report += self._summary()
        report += self._services_by_vendor_and_category()
        report += self._detailed_resources_by_vendor()
        report += self._footer()
        
        return report

    def generate_json(self) -> str:
        """
        Generate a JSON report.
        
        Returns:
            JSON formatted report as string
        """
        # Build services without instance details for JSON output
        services_no_instances: Dict[str, Dict] = {}
        for category, services in self.services.items():
            services_no_instances[category] = {}
            for service_name, info in services.items():
                filtered = {k: v for k, v in info.items() if k != 'instances'}
                services_no_instances[category][service_name] = filtered

        # Prepare metadata and optionally handle parsed_files section
        metadata_copy = dict(self.metadata) if self.metadata else {}
        parsed_files = metadata_copy.get('parsed_files') if self.include_parsed_files else None
        if not self.include_parsed_files and 'parsed_files' in metadata_copy:
            metadata_copy.pop('parsed_files', None)

        # Build vendor grouping for JSON
        vendors_grouped: Dict[str, Dict] = {'Azure': {}, 'AWS': {}}
        for category, services in self.services.items():
            for service_name, info in services.items():
                vendor = self._get_vendor(info.get('resource_type', ''))
                if vendor not in vendors_grouped:
                    continue
                if category not in vendors_grouped[vendor]:
                    vendors_grouped[vendor][category] = {}
                vendors_grouped[vendor][category][service_name] = {
                    'resource_type': info.get('resource_type'),
                    'count': info.get('count', 0)
                }

        # Compose JSON in desired order: generated, summary, metadata, services, vendors
        report_data = {
            'generated': datetime.now().isoformat(),
            'summary': self._get_summary_stats(),
            'metadata': metadata_copy,
            'services': services_no_instances,
            'vendors': vendors_grouped,
        }
        # Keep parsed_files in metadata for compatibility and append at end for readability
        if self.include_parsed_files and parsed_files:
            report_data['metadata']['parsed_files'] = parsed_files
            report_data['parsed_files'] = parsed_files
        return json.dumps(report_data, indent=2)

    def _header(self) -> str:
        """Generate report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = "# Cloud Services Assessment Report\n"
        if self.include_legacy_header:
            header += "# Azure Services Assessment Report\n"
        return f"""{header}

**Generated:** {timestamp}

---

"""

    def _metadata_section(self) -> str:
        """Generate metadata section if available"""
        if not self.metadata:
            return ""
        section = "## Analysis Metadata\n\n"
        # Parsed files: show only counts per type
        parsed = self.metadata.get('parsed_files', {})
        if parsed:
            tf_files = parsed.get('terraform', [])
            bicep_files = parsed.get('bicep', [])
            ps_files = parsed.get('powershell', [])
            cli_files = parsed.get('azure_cli', [])
            arm_files = parsed.get('arm_template', [])
            cf_files = parsed.get('cloudformation', [])
            py_files = parsed.get('python', [])
            bash_files = parsed.get('bash', [])
            ts_files = parsed.get('typescript', [])
            go_files = parsed.get('go', [])
            java_files = parsed.get('java', [])
            total = sum(len(lst) for lst in [tf_files,bicep_files,ps_files,cli_files,arm_files,cf_files,py_files,bash_files,ts_files,go_files,java_files])
            section += f"**Files Analyzed:** {total}\n\n"
        return section

    def _summary(self) -> str:
        """Generate summary section"""
        stats = self._get_summary_stats()
        
        summary = "## Summary\n\n"
        summary += f"- **Total Service Categories:** {stats['categories']}\n"
        summary += f"- **Total Azure Services:** {stats['azure_services']}\n"
        summary += f"- **Total AWS Services:** {stats['aws_services']}\n"
        summary += f"- **Total Resources:** {stats['resources']}\n"
        summary += "\n"
        
        # Add file type breakdown if available
        parsed = self.metadata.get('parsed_files', {})
        if parsed:
            tf_count = len(parsed.get('terraform', []))
            bicep_count = len(parsed.get('bicep', []));
            
            if tf_count or bicep_count:
                summary += "**Files Analyzed:**\n\n"
                if tf_count:
                    summary += f"- Terraform Files: {tf_count}\n"
                if bicep_count:
                    summary += f"- Bicep Files: {bicep_count}\n"
                summary += "\n"
        
        return summary

    def _get_vendor(self, resource_type: str) -> str:
        rt = (resource_type or '').lower()
        if rt.startswith('azurerm_') or rt.startswith('microsoft.'):
            return 'Azure'
        if rt.startswith('aws_') or rt.startswith('aws::'):
            return 'AWS'
        return 'Other'

    def _split_services_by_vendor(self):
        vendors = {'Azure': {}, 'AWS': {}, 'Other': {}}
        for category, services in self.services.items():
            for service_name, info in services.items():
                vendor = self._get_vendor(info.get('resource_type', ''))
                if category not in vendors[vendor]:
                    vendors[vendor][category] = {}
                vendors[vendor][category][service_name] = info
        return vendors

    def _services_by_vendor_and_category(self) -> str:
        vendors = self._split_services_by_vendor()
        report = "## Services by Cloud Vendor\n\n"
        for vendor in ['Azure', 'AWS']:
            vendor_services = vendors[vendor]
            if not vendor_services:
                continue
            report += f"### {vendor}\n\n"
            for category in sorted(vendor_services.keys()):
                report += f"#### {category}\n\n"
                for service_name in sorted(vendor_services[category].keys()):
                    info = vendor_services[category][service_name]
                    count = info.get('count', 0)
                    report += f"- **{service_name}** ({info.get('resource_type','')}): {count} resource(s)\n"
                report += "\n"
            report += "\n"
        return report

    def _detailed_resources_by_vendor(self) -> str:
        vendors = self._split_services_by_vendor()
        report = "## Detailed Resource List by Cloud Vendor\n\n"
        for vendor in ['Azure', 'AWS']:
            vendor_services = vendors[vendor]
            if not vendor_services:
                continue
            report += f"### {vendor}\n\n"
            for category in sorted(vendor_services.keys()):
                report += f"#### {category}\n\n"
                for service_name in sorted(vendor_services[category].keys()):
                    info = vendor_services[category][service_name]
                    instances = info.get('instances', [])
                    report += f"##### {service_name}\n\n"
                    report += f"**Type:** `{info.get('resource_type','')}`\n\n"
                    report += f"**Count:** {len(instances) if instances else info.get('count', 0)}\n\n"
                    if instances:
                        report += "**Instances:**\n\n"
                        for instance in sorted(instances):
                            report += f"- `{instance}`\n"
                        report += "\n"
                report += "\n"
            report += "\n"
        return report

    def _footer(self) -> str:
        """Generate report footer"""
        footer = "---\n\n"
        footer += "**Note:** This report was automatically generated by analyzing Infrastructure as Code files.\n\n"
        footer += "**Supported Formats:**\n"
        footer += "- Terraform (.tf files)\n"
        footer += "- Bicep (.bicep files)\n\n"
        footer += "For production assessments, ensure all Infrastructure as Code files are included in the analysis.\n"
        
        return footer

    def _get_summary_stats(self) -> Dict[str, int]:
        """Calculate summary statistics"""
        total_services = sum(len(services) for services in self.services.values())
        total_resources = sum(
            service['count'] for category in self.services.values()
            for service in category.values()
        )
        categories = len(self.services)

        # Count services per vendor
        azure_services = 0
        aws_services = 0
        for category, services in self.services.items():
            for _, info in services.items():
                vendor = self._get_vendor(info.get('resource_type', ''))
                if vendor == 'Azure':
                    azure_services += 1
                elif vendor == 'AWS':
                    aws_services += 1
        
        return {
            'categories': categories,
            'services': total_services,
            'resources': total_resources,
            'azure_services': azure_services,
            'aws_services': aws_services,
        }

    def save_to_file(self, output_file: str, format: str = 'markdown') -> None:
        """
        Save report to file.
        
        Args:
            output_file: Output file path
            format: Report format ('markdown' or 'json')
        """
        if format == 'json':
            content = self.generate_json()
        else:
            content = self.generate_markdown()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Report saved to: {output_file}")
