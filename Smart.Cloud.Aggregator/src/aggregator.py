#!/usr/bin/env python3
"""
Terraform Azure Service Aggregator

This tool assesses Terraform configurations and generates a report of all Azure 
services used in the solution, outputting results to a markdown file.

Main module - Contains TerraformParser and ReportGenerator classes.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AzureService:
    """Represents an Azure service resource"""
    resource_type: str
    provider: str
    count: int
    instances: List[str]
    resource_group: str = "N/A"

    def to_dict(self) -> Dict:
        return asdict(self)


class TerraformParser:
    """Parses Terraform files and extracts Azure resource information"""

    # Mapping of Terraform Azure provider resource types to service categories
    SERVICE_MAPPING = {
        # Compute Services
        'azurerm_virtual_machine': ('Compute', 'Virtual Machines'),
        'azurerm_linux_virtual_machine': ('Compute', 'Virtual Machines'),
        'azurerm_windows_virtual_machine': ('Compute', 'Virtual Machines'),
        'azurerm_app_service': ('Compute', 'App Service'),
        'azurerm_app_service_plan': ('Compute', 'App Service Plan'),
        'azurerm_function_app': ('Compute', 'Functions'),
        'azurerm_container_registry': ('Compute', 'Container Registry'),
        'azurerm_container_group': ('Compute', 'Container Instances'),
        'azurerm_kubernetes_cluster': ('Compute', 'AKS'),

        # Storage Services
        'azurerm_storage_account': ('Storage', 'Storage Account'),
        'azurerm_storage_container': ('Storage', 'Blob Storage'),
        'azurerm_storage_share': ('Storage', 'File Share'),
        'azurerm_data_lake_store': ('Storage', 'Data Lake Storage'),

        # Database Services
        'azurerm_sql_server': ('Database', 'SQL Server'),
        'azurerm_sql_database': ('Database', 'SQL Database'),
        'azurerm_postgresql_server': ('Database', 'PostgreSQL'),
        'azurerm_mysql_server': ('Database', 'MySQL'),
        'azurerm_mariadb_server': ('Database', 'MariaDB'),
        'azurerm_cosmosdb_account': ('Database', 'Cosmos DB'),
        'azurerm_redis_cache': ('Database', 'Azure Cache for Redis'),

        # Networking Services
        'azurerm_virtual_network': ('Networking', 'Virtual Network'),
        'azurerm_subnet': ('Networking', 'Subnet'),
        'azurerm_network_security_group': ('Networking', 'Network Security Group'),
        'azurerm_public_ip': ('Networking', 'Public IP'),
        'azurerm_network_interface': ('Networking', 'Network Interface'),
        'azurerm_load_balancer': ('Networking', 'Load Balancer'),
        'azurerm_application_gateway': ('Networking', 'Application Gateway'),
        'azurerm_vpn_gateway': ('Networking', 'VPN Gateway'),
        'azurerm_express_route_circuit': ('Networking', 'ExpressRoute'),
        'azurerm_traffic_manager_profile': ('Networking', 'Traffic Manager'),
        'azurerm_frontdoor': ('Networking', 'Front Door'),
        'azurerm_private_endpoint': ('Networking', 'Private Endpoint'),

        # Identity & Security
        'azurerm_key_vault': ('Security', 'Key Vault'),
        'azurerm_key_vault_secret': ('Security', 'Key Vault Secret'),
        'azurerm_key_vault_key': ('Security', 'Key Vault Key'),
        'azurerm_user_assigned_identity': ('Security', 'Managed Identity'),
        'azurerm_role_assignment': ('Security', 'Role Assignment'),

        # Monitoring & Analytics
        'azurerm_log_analytics_workspace': ('Monitoring', 'Log Analytics'),
        'azurerm_application_insights': ('Monitoring', 'Application Insights'),
        'azurerm_monitor_metric_alert': ('Monitoring', 'Metric Alert'),
        'azurerm_monitor_action_group': ('Monitoring', 'Action Group'),

        # Integration Services
        'azurerm_api_management': ('Integration', 'API Management'),
        'azurerm_service_bus_namespace': ('Integration', 'Service Bus'),
        'azurerm_eventhub_namespace': ('Integration', 'Event Hubs'),
        'azurerm_logic_app_workflow': ('Integration', 'Logic Apps'),

        # AI & Machine Learning
        'azurerm_cognitive_account': ('AI/ML', 'Cognitive Services'),
        'azurerm_machine_learning_workspace': ('AI/ML', 'Machine Learning'),
        'azurerm_search_service': ('AI/ML', 'Cognitive Search'),

        # Management & Governance
        'azurerm_resource_group': ('Management', 'Resource Group'),
        'azurerm_management_lock': ('Management', 'Management Lock'),
        'azurerm_policy_assignment': ('Management', 'Policy Assignment'),
        'azurerm_automation_account': ('Management', 'Automation Account'),

        # Data Services
        'azurerm_data_factory': ('Data', 'Data Factory'),
        'azurerm_synapse_workspace': ('Data', 'Synapse Analytics'),
        'azurerm_stream_analytics_job': ('Data', 'Stream Analytics'),
    }

    def __init__(self):
        self.resources: Dict[str, List[str]] = defaultdict(list)
        self.resource_groups: Set[str] = set()

    def parse_terraform_files(self, terraform_dir: str) -> Dict[str, Dict]:
        """
        Parse all Terraform files in a directory
        
        Args:
            terraform_dir: Path to directory containing Terraform files
            
        Returns:
            Dictionary of aggregated Azure services
        """
        terraform_path = Path(terraform_dir)
        
        if not terraform_path.exists():
            raise FileNotFoundError(f"Terraform directory not found: {terraform_dir}")

        # Find all .tf files
        tf_files = list(terraform_path.glob('**/*.tf'))
        
        if not tf_files:
            raise FileNotFoundError(f"No Terraform files found in {terraform_dir}")

        print(f"Found {len(tf_files)} Terraform file(s)")

        # Parse each file
        for tf_file in tf_files:
            self._parse_file(tf_file)

        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        """Parse a single Terraform file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self._extract_resources(content, file_path)
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _extract_resources(self, content: str, file_path: Path) -> None:
        """Extract Azure resources from Terraform configuration"""
        # Pattern to match resource blocks: resource "type" "name"
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
        
        matches = re.finditer(resource_pattern, content)
        
        for match in matches:
            resource_type = match.group(1)
            resource_name = match.group(2)
            
            if resource_type.startswith('azurerm_'):
                full_resource_id = f"{resource_type}.{resource_name}"
                self.resources[resource_type].append(full_resource_id)

                # Try to extract resource group
                resource_section = self._extract_resource_section(
                    content, match.start()
                )
                rg = self._extract_resource_group(resource_section)
                if rg:
                    self.resource_groups.add(rg)

    def _extract_resource_section(self, content: str, start_pos: int) -> str:
        """Extract the resource configuration section"""
        brace_count = 0
        in_section = False
        section_start = start_pos
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                if not in_section:
                    in_section = True
                    section_start = i
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if in_section and brace_count == 0:
                    return content[section_start:i+1]
        
        return ""

    def _extract_resource_group(self, resource_section: str) -> str:
        """Extract resource group name from resource configuration"""
        # Look for resource_group_name
        rg_match = re.search(
            r'resource_group_name\s*=\s*["\']?([^"\'\n}]+)["\']?',
            resource_section
        )
        if rg_match:
            return rg_match.group(1).strip().strip('"').strip("'")
        return ""

    def _aggregate_services(self) -> Dict[str, Dict]:
        """Aggregate resources by service category"""
        aggregated: Dict[str, Dict] = defaultdict(lambda: defaultdict(list))
        
        for resource_type, instances in self.resources.items():
            if resource_type in self.SERVICE_MAPPING:
                category, service_name = self.SERVICE_MAPPING[resource_type]
                
                aggregated[category][service_name] = {
                    'resource_type': resource_type,
                    'count': len(instances),
                    'instances': instances
                }
        
        return dict(aggregated)


class ReportGenerator:
    """Generates markdown reports of Azure services"""

    def __init__(self, aggregated_services: Dict[str, Dict]):
        self.services = aggregated_services

    def generate_markdown(self) -> str:
        """Generate a comprehensive markdown report"""
        report = self._header()
        report += self._summary()
        report += self._services_by_category()
        report += self._detailed_resources()
        report += self._footer()
        
        return report

    def _header(self) -> str:
        """Generate report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Azure Services Assessment Report

**Generated:** {timestamp}

---

"""

    def _summary(self) -> str:
        """Generate summary section"""
        total_services = sum(
            len(services) for services in self.services.values()
        )
        total_resources = sum(
            service['count'] for category in self.services.values()
            for service in category.values()
        )
        categories = len(self.services)

        return f"""## Summary

- **Total Service Categories:** {categories}
- **Total Azure Services:** {total_services}
- **Total Resources:** {total_resources}

---

"""

    def _services_by_category(self) -> str:
        """Generate services organized by category"""
        report = "## Azure Services by Category\n\n"
        
        for category in sorted(self.services.keys()):
            services = self.services[category]
            report += f"### {category}\n\n"
            
            for service_name in sorted(services.keys()):
                service_info = services[service_name]
                count = service_info['count']
                report += f"- **{service_name}** ({service_info['resource_type']}): {count} resource(s)\n"
            
            report += "\n"
        
        return report

    def _detailed_resources(self) -> str:
        """Generate detailed resource list"""
        report = "## Detailed Resource List\n\n"
        
        for category in sorted(self.services.keys()):
            services = self.services[category]
            report += f"### {category}\n\n"
            
            for service_name in sorted(services.keys()):
                service_info = services[service_name]
                instances = service_info['instances']
                
                report += f"#### {service_name}\n\n"
                report += f"**Type:** `{service_info['resource_type']}`\n\n"
                report += "**Instances:**\n\n"
                
                for instance in sorted(instances):
                    report += f"- `{instance}`\n"
                
                report += "\n"
        
        return report

    def _footer(self) -> str:
        """Generate report footer"""
        return """---

**Note:** This report was automatically generated by analyzing Terraform configurations.
For production assessments, ensure all Terraform files are included in the analysis.
"""

    def save_to_file(self, output_file: str) -> None:
        """Save report to markdown file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown())
        print(f"Report saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Assess Terraform configurations and aggregate Azure services'
    )
    
    parser.add_argument(
        'terraform_dir',
        help='Path to Terraform directory or file'
    )
    parser.add_argument(
        '-o', '--output',
        default='azure_services_report.md',
        help='Output markdown file (default: azure_services_report.md)'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Also output results as JSON'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        print(f"Analyzing Terraform configurations in: {args.terraform_dir}")
        
        # Parse Terraform files
        parser_obj = TerraformParser()
        aggregated = parser_obj.parse_terraform_files(args.terraform_dir)

        if not aggregated:
            print("No Azure resources found in Terraform files.")
            return

        # Generate markdown report
        report_gen = ReportGenerator(aggregated)
        report_gen.save_to_file(args.output)

        # Optionally generate JSON output
        if args.json:
            json_output = args.output.replace('.md', '.json')
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(aggregated, f, indent=2)
            print(f"JSON output saved to: {json_output}")

        # Print summary
        if args.verbose:
            print("\n" + "="*60)
            print(report_gen.generate_markdown())
            print("="*60)
        else:
            total_resources = sum(
                service['count'] for category in aggregated.values()
                for service in category.values()
            )
            print(f"\n? Analysis complete: Found {total_resources} Azure resource(s)")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
