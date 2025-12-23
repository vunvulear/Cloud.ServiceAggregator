"""
Service Mapping Module

Defines the mapping of IaC resource types to Azure and AWS service categories.
Shared between Terraform and Bicep parsers.
"""

from typing import Dict, Tuple, Optional
import re

# Service mapping: resource_type -> (category, service_name)
SERVICE_MAPPING: Dict[str, Tuple[str, str]] = {
    # Compute Services
    'azurerm_virtual_machine': ('Compute', 'Virtual Machines'),
    'Microsoft.Compute/virtualMachines': ('Compute', 'Virtual Machines'),
    
    'azurerm_linux_virtual_machine': ('Compute', 'Virtual Machines'),
    'azurerm_windows_virtual_machine': ('Compute', 'Virtual Machines'),
    
    'azurerm_app_service': ('Compute', 'App Service'),
    'Microsoft.Web/sites': ('Compute', 'App Service'),
    
    'azurerm_app_service_plan': ('Compute', 'App Service Plan'),
    'Microsoft.Web/serverfarms': ('Compute', 'App Service Plan'),
    
    'azurerm_function_app': ('Compute', 'Functions'),
    'Microsoft.Web/sites@2021-02-01': ('Compute', 'Functions'),
    
    'azurerm_container_registry': ('Compute', 'Container Registry'),
    'Microsoft.ContainerRegistry/registries': ('Compute', 'Container Registry'),
    
    'azurerm_container_group': ('Compute', 'Container Instances'),
    'Microsoft.ContainerInstance/containerGroups': ('Compute', 'Container Instances'),
    
    'azurerm_kubernetes_cluster': ('Compute', 'AKS'),
    'Microsoft.ContainerService/managedClusters': ('Compute', 'AKS'),

    # Additional Azure services (expanded)
    # AI/ML and Bots
    'Microsoft.BotService/botServices': ('AI/ML', 'Azure AI Bot Service'),
    'Microsoft.HealthBot/healthBots': ('AI/ML', 'Health Bot'),
    # Data/Analytics
    'Microsoft.Kusto/clusters': ('Data', 'Azure Data Explorer'),
    'Microsoft.HDInsight/clusters': ('Data', 'HDInsight'),
    'Microsoft.PowerBIDedicated/capacities': ('Data', 'Power BI Embedded'),
    'Microsoft.Purview/accounts': ('Data', 'Microsoft Purview'),
    'Microsoft.DataShare/accounts': ('Data', 'Azure Data Share'),
    'Microsoft.Databricks/workspaces': ('Data', 'Azure Databricks'),
    # Compute
    'Microsoft.Compute/virtualMachineScaleSets': ('Compute', 'Virtual Machine Scale Sets'),
    'Microsoft.Compute/hosts': ('Compute', 'Dedicated Host'),
    'Microsoft.Batch/batchAccounts': ('Compute', 'Azure Batch'),
    'Microsoft.AppPlatform/Spring': ('Compute', 'Azure Spring Apps'),
    'Microsoft.AVS/privateClouds': ('Compute', 'Azure VMware Solution'),
    'Microsoft.Quantum/workspaces': ('Compute', 'Azure Quantum'),
    'Microsoft.Compute/cloudServices': ('Compute', 'Cloud Services'),
    'Microsoft.DesktopVirtualization/hostPools': ('Compute', 'Azure Virtual Desktop'),
    'Microsoft.Web/staticSites': ('Compute', 'Static Web Apps'),
    'Microsoft.VirtualMachineImages/imageTemplates': ('Compute', 'Azure VM Image Builder'),
    # Containers
    'Microsoft.ContainerService/fleets': ('Compute', 'Azure Kubernetes Fleet Manager'),
    'Microsoft.RedHatOpenShift/openshiftClusters': ('Compute', 'Azure Red Hat OpenShift'),
    'Microsoft.App/containerApps': ('Compute', 'Azure Container Apps'),
    'Microsoft.App/managedEnvironments': ('Compute', 'Azure Container Apps'),
    'Microsoft.AppConfiguration/configurationStores': ('Integration', 'App Configuration'),
    # Databases
    'Microsoft.Sql/managedInstances': ('Database', 'SQL Managed Instance'),
    'Microsoft.Cache/redisEnterprise': ('Database', 'Azure Managed Redis'),
    # Developer/DevTest
    'Microsoft.DevTestLab/labs': ('Management', 'DevTest Labs'),
    'Microsoft.DeploymentEnvironments/projects': ('Management', 'Deployment Environments'),
    # Integration/Eventing
    'Microsoft.EventGrid/topics': ('Integration', 'Event Grid'),
    'Microsoft.EventGrid/domains': ('Integration', 'Event Grid'),
    'Microsoft.EventGrid/systemTopics': ('Integration', 'Event Grid'),
    # IoT
    'Microsoft.Devices/IotHubs': ('Integration', 'IoT Hub'),
    'Microsoft.IoTCentral/iotApps': ('Integration', 'IoT Central'),
    'Microsoft.DigitalTwins/digitalTwinsInstances': ('Integration', 'Digital Twins'),
    'Microsoft.TimeSeriesInsights/environments': ('Integration', 'Time Series Insights'),
    # Management + Governance
    'Microsoft.CostManagement/exports': ('Management', 'Cost Management'),
    'Microsoft.Advisor/configurations': ('Management', 'Azure Advisor'),
    'Microsoft.HybridCompute/machines': ('Management', 'Azure Arc'),
    'Microsoft.Kubernetes/connectedClusters': ('Management', 'Azure Arc'),
    'Microsoft.Blueprint/blueprints': ('Management', 'Blueprints'),
    # Media & Communications
    'Microsoft.Media/mediaservices': ('Integration', 'Media Services'),
    'Microsoft.Communication/communicationServices': ('Integration', 'Communication Services'),
    # Migration
    'Microsoft.Migrate/migrateProjects': ('Management', 'Azure Migrate'),
    'Microsoft.RecoveryServices/vaults': ('Management', 'Azure Site Recovery'),
    'Microsoft.DataMigration/services': ('Management', 'Database Migration Service'),
    'Microsoft.DataBoxEdge/dataBoxEdgeDevices': ('Storage', 'Azure Stack Edge'),
    'Microsoft.DataBox/jobs': ('Storage', 'Azure Data Box'),
    # Mobile / Realtime
    'Microsoft.NotificationHubs/namespaces/notificationHubs': ('Integration', 'Notification Hubs'),
    'Microsoft.SignalRService/signalR': ('Integration', 'Azure SignalR Service'),
    'Microsoft.SignalRService/webPubSub': ('Integration', 'Azure Web PubSub'),
    # Networking additions
    'Microsoft.Network/dnsZones': ('Networking', 'DNS'),
    'Microsoft.Network/azureFirewalls': ('Networking', 'Azure Firewall'),
    'Microsoft.Network/natGateways': ('Networking', 'NAT Gateway'),
    'Microsoft.Network/bastionHosts': ('Networking', 'Bastion'),
    'Microsoft.Network/privateLinkServices': ('Networking', 'Private Link'),
    # Security
    'Microsoft.Security/pricings': ('Security', 'Microsoft Defender for Cloud'),
    'Microsoft.IoTSecurity/defenderSettings': ('Security', 'Microsoft Defender for IoT'),
    'Microsoft.Network/ddosProtectionPlans': ('Security', 'Azure DDoS Protection'),
    'Microsoft.ConfidentialLedger/ledgers': ('Security', 'Azure Confidential Ledger'),
    'Microsoft.HardwareSecurityModules/dedicatedHSMs': ('Security', 'Azure Cloud HSM'),
    'Microsoft.Attestation/attestationProviders': ('Security', 'Azure Attestation'),
    'Microsoft.SecurityInsights/alertRules': ('Security', 'Microsoft Sentinel'),
    # Storage
    'Microsoft.Compute/disks': ('Storage', 'Disk Storage'),
    'Microsoft.NetApp/netAppAccounts/capacityPools/volumes': ('Storage', 'Azure NetApp Files'),
    'Microsoft.StorageSync/storageSyncServices': ('Storage', 'Azure File Sync'),
    'Microsoft.ElasticSan/elasticSans': ('Storage', 'Azure Elastic SAN'),
    'Microsoft.StorageActions/storageTasks': ('Storage', 'Azure Storage Actions'),

    # Storage Services
    'azurerm_storage_account': ('Storage', 'Storage Account'),
    'Microsoft.Storage/storageAccounts': ('Storage', 'Storage Account'),
    
    'azurerm_storage_container': ('Storage', 'Blob Storage'),
    'Microsoft.Storage/storageAccounts/blobServices/containers': ('Storage', 'Blob Storage'),
    
    'azurerm_storage_share': ('Storage', 'File Share'),
    'Microsoft.Storage/storageAccounts/fileServices/shares': ('Storage', 'File Share'),
    
    'azurerm_data_lake_store': ('Storage', 'Data Lake Storage'),
    'Microsoft.DataLakeStore/accounts': ('Storage', 'Data Lake Storage'),

    # Database Services
    'azurerm_sql_server': ('Database', 'SQL Server'),
    'Microsoft.Sql/servers': ('Database', 'SQL Server'),
    
    'azurerm_sql_database': ('Database', 'SQL Database'),
    'Microsoft.Sql/servers/databases': ('Database', 'SQL Database'),
    
    'azurerm_postgresql_server': ('Database', 'PostgreSQL'),
    'Microsoft.DBforPostgreSQL/servers': ('Database', 'PostgreSQL'),
    
    'azurerm_mysql_server': ('Database', 'MySQL'),
    'Microsoft.DBforMySQL/servers': ('Database', 'MySQL'),
    
    'azurerm_mariadb_server': ('Database', 'MariaDB'),
    'Microsoft.DBforMariaDB/servers': ('Database', 'MariaDB'),
    
    'azurerm_cosmosdb_account': ('Database', 'Cosmos DB'),
    'Microsoft.DocumentDB/databaseAccounts': ('Database', 'Cosmos DB'),
    
    'azurerm_redis_cache': ('Database', 'Azure Cache for Redis'),
    'Microsoft.Cache/redis': ('Database', 'Azure Cache for Redis'),

    # Networking Services
    'azurerm_virtual_network': ('Networking', 'Virtual Network'),
    'Microsoft.Network/virtualNetworks': ('Networking', 'Virtual Network'),
    
    'azurerm_subnet': ('Networking', 'Subnet'),
    'Microsoft.Network/virtualNetworks/subnets': ('Networking', 'Subnet'),
    
    'azurerm_network_security_group': ('Networking', 'Network Security Group'),
    'Microsoft.Network/networkSecurityGroups': ('Networking', 'Network Security Group'),
    
    'azurerm_public_ip': ('Networking', 'Public IP'),
    'Microsoft.Network/publicIPAddresses': ('Networking', 'Public IP'),
    
    'azurerm_network_interface': ('Networking', 'Network Interface'),
    'Microsoft.Network/networkInterfaces': ('Networking', 'Network Interface'),
    
    'azurerm_load_balancer': ('Networking', 'Load Balancer'),
    'Microsoft.Network/loadBalancers': ('Networking', 'Load Balancer'),
    
    'azurerm_application_gateway': ('Networking', 'Application Gateway'),
    'Microsoft.Network/applicationGateways': ('Networking', 'Application Gateway'),
    
    'azurerm_vpn_gateway': ('Networking', 'VPN Gateway'),
    'Microsoft.Network/vpnGateways': ('Networking', 'VPN Gateway'),
    
    'azurerm_express_route_circuit': ('Networking', 'ExpressRoute'),
    'Microsoft.Network/expressRouteCircuits': ('Networking', 'ExpressRoute'),
    
    'azurerm_traffic_manager_profile': ('Networking', 'Traffic Manager'),
    'Microsoft.Network/trafficManagerProfiles': ('Networking', 'Traffic Manager'),
    
    'azurerm_frontdoor': ('Networking', 'Front Door'),
    'Microsoft.Network/frontDoors': ('Networking', 'Front Door'),
    
    'azurerm_private_endpoint': ('Networking', 'Private Endpoint'),
    'Microsoft.Network/privateEndpoints': ('Networking', 'Private Endpoint'),

    # Identity & Security
    'azurerm_key_vault': ('Security', 'Key Vault'),
    'Microsoft.KeyVault/vaults': ('Security', 'Key Vault'),
    
    'azurerm_key_vault_secret': ('Security', 'Key Vault Secret'),
    'Microsoft.KeyVault/vaults/secrets': ('Security', 'Key Vault Secret'),
    
    'azurerm_key_vault_key': ('Security', 'Key Vault Key'),
    'Microsoft.KeyVault/vaults/keys': ('Security', 'Key Vault Key'),
    
    'azurerm_user_assigned_identity': ('Security', 'Managed Identity'),
    'Microsoft.ManagedIdentity/userAssignedIdentities': ('Security', 'Managed Identity'),
    
    'azurerm_role_assignment': ('Security', 'Role Assignment'),
    'Microsoft.Authorization/roleAssignments': ('Security', 'Role Assignment'),

    # Monitoring & Analytics
    'azurerm_log_analytics_workspace': ('Monitoring', 'Log Analytics'),
    'Microsoft.OperationalInsights/workspaces': ('Monitoring', 'Log Analytics'),
    
    'azurerm_application_insights': ('Monitoring', 'Application Insights'),
    'Microsoft.Insights/components': ('Monitoring', 'Application Insights'),
    
    'azurerm_monitor_metric_alert': ('Monitoring', 'Metric Alert'),
    'Microsoft.Insights/metricAlerts': ('Monitoring', 'Metric Alert'),
    
    'azurerm_monitor_action_group': ('Monitoring', 'Action Group'),
    'Microsoft.Insights/actionGroups': ('Monitoring', 'Action Group'),

    # Integration Services
    'azurerm_api_management': ('Integration', 'API Management'),
    'Microsoft.ApiManagement/service': ('Integration', 'API Management'),
    
    'azurerm_service_bus_namespace': ('Integration', 'Service Bus'),
    'Microsoft.ServiceBus/namespaces': ('Integration', 'Service Bus'),
    
    'azurerm_eventhub_namespace': ('Integration', 'Event Hubs'),
    'Microsoft.EventHub/namespaces': ('Integration', 'Event Hubs'),
    
    'azurerm_logic_app_workflow': ('Integration', 'Logic Apps'),
    'Microsoft.Logic/workflows': ('Integration', 'Logic Apps'),

    # AI & Machine Learning
    'azurerm_cognitive_account': ('AI/ML', 'Cognitive Services'),
    'Microsoft.CognitiveServices/accounts': ('AI/ML', 'Cognitive Services'),

    # AI + Machine Learning (Cognitive Services kinds via synthetic keys)
    'Microsoft.CognitiveServices/OpenAI': ('AI/ML', 'Azure OpenAI Service'),
    'Microsoft.CognitiveServices/Vision': ('AI/ML', 'Azure AI Vision'),
    'Microsoft.CognitiveServices/Speech': ('AI/ML', 'Azure AI Speech'),
    'Microsoft.CognitiveServices/Language': ('AI/ML', 'Azure AI Language'),
    'Microsoft.CognitiveServices/DocumentIntelligence': ('AI/ML', 'Azure AI Document Intelligence'),
    'Microsoft.CognitiveServices/MetricsAdvisor': ('AI/ML', 'Azure AI Metrics Advisor'),
    'Microsoft.CognitiveServices/Personalizer': ('AI/ML', 'Azure AI Personalizer'),
    'Microsoft.CognitiveServices/ContentSafety': ('AI/ML', 'Content Safety'),

    # Management & Governance
    'azurerm_resource_group': ('Management', 'Resource Group'),
    'Microsoft.Resources/resourceGroups': ('Management', 'Resource Group'),
    
    'azurerm_management_lock': ('Management', 'Management Lock'),
    'Microsoft.Authorization/locks': ('Management', 'Management Lock'),
    
    'azurerm_policy_assignment': ('Management', 'Policy Assignment'),
    'Microsoft.Authorization/policyAssignments': ('Management', 'Policy Assignment'),
    
    'azurerm_automation_account': ('Management', 'Automation Account'),
    'Microsoft.Automation/automationAccounts': ('Management', 'Automation Account'),

    # Data Services
    'azurerm_data_factory': ('Data', 'Data Factory'),
    'Microsoft.DataFactory/factories': ('Data', 'Data Factory'),
    
    'azurerm_synapse_workspace': ('Data', 'Synapse Analytics'),
    'Microsoft.Synapse/workspaces': ('Data', 'Synapse Analytics'),
    
    'azurerm_stream_analytics_job': ('Data', 'Stream Analytics'),
    'Microsoft.StreamAnalytics/streamingjobs': ('Data', 'Stream Analytics'),

    # --- AWS Terraform resource mappings ---
    # Compute
    'aws_instance': ('Compute', 'EC2 Instance'),
    'aws_lambda_function': ('Compute', 'Lambda Function'),
    'aws_eks_cluster': ('Compute', 'EKS Cluster'),

    # Storage
    'aws_s3_bucket': ('Storage', 'S3 Bucket'),
    'aws_ebs_volume': ('Storage', 'EBS Volume'),

    # Database
    'aws_db_instance': ('Database', 'RDS Instance'),
    'aws_rds_cluster': ('Database', 'RDS Cluster'),
    'aws_dynamodb_table': ('Database', 'DynamoDB Table'),

    # Networking
    'aws_vpc': ('Networking', 'VPC'),
    'aws_subnet': ('Networking', 'Subnet'),
    'aws_security_group': ('Networking', 'Security Group'),
    'aws_internet_gateway': ('Networking', 'Internet Gateway'),
    'aws_nat_gateway': ('Networking', 'NAT Gateway'),
    'aws_lb': ('Networking', 'Load Balancer'),
    'aws_alb': ('Networking', 'Application Load Balancer'),
    'aws_elb': ('Networking', 'Classic Load Balancer'),

    # Identity & Access
    'aws_iam_role': ('Security', 'IAM Role'),
    'aws_iam_policy': ('Security', 'IAM Policy'),
    'aws_iam_user': ('Security', 'IAM User'),
    'aws_iam_group': ('Security', 'IAM Group'),

    # TypeScript/Go/Java normalized keys (map to same categories)
    'aws_ec2_instance': ('Compute', 'EC2 Instance'),
    'aws_s3_bucket': ('Storage', 'S3 Bucket'),
    'aws_lambda_function': ('Compute', 'Lambda Function'),
    'aws_dynamodb_table': ('Database', 'DynamoDB Table'),
    'aws_rds_instance': ('Database', 'RDS Instance'),

    # --- Expanded AWS resource mappings ---
    # Compute & Containers
    'aws_launch_template': ('Compute', 'EC2 Launch Template'),
    'aws_autoscaling_group': ('Compute', 'Auto Scaling Group'),
    'aws_ecs_cluster': ('Compute', 'ECS Cluster'),
    'aws_ecs_service': ('Compute', 'ECS Service'),
    'aws_ecs_task_definition': ('Compute', 'ECS Task Definition'),
    'aws_ecr_repository': ('Compute', 'ECR Repository'),
    'aws_batch_job_queue': ('Compute', 'AWS Batch'),
    'aws_batch_compute_environment': ('Compute', 'AWS Batch'),
    'aws_lightsail_instance': ('Compute', 'Lightsail Instance'),

    # Serverless
    'aws_lambda_layer_version': ('Compute', 'Lambda Layer'),
    'aws_api_gateway_rest_api': ('Integration', 'API Gateway'),
    'aws_apigatewayv2_api': ('Integration', 'API Gateway v2'),

    # Storage & Content Delivery
    'aws_s3_bucket_policy': ('Storage', 'S3 Bucket Policy'),
    'aws_s3_object': ('Storage', 'S3 Object'),
    'aws_efs_file_system': ('Storage', 'EFS File System'),
    'aws_efs_mount_target': ('Storage', 'EFS Mount Target'),
    'aws_fsx_lustre_file_system': ('Storage', 'FSx for Lustre'),
    'aws_fsx_windows_file_system': ('Storage', 'FSx for Windows'),
    'aws_s3_bucket_lifecycle_configuration': ('Storage', 'S3 Lifecycle'),
    'aws_cloudfront_distribution': ('Networking', 'CloudFront Distribution'),

    # Databases & Analytics
    'aws_rds_cluster_instance': ('Database', 'RDS Cluster Instance'),
    'aws_rds_global_cluster': ('Database', 'RDS Global Cluster'),
    'aws_neptune_cluster': ('Database', 'Neptune Cluster'),
    'aws_neptune_cluster_instance': ('Database', 'Neptune Instance'),
    'aws_docdb_cluster': ('Database', 'DocumentDB Cluster'),
    'aws_docdb_cluster_instance': ('Database', 'DocumentDB Instance'),
    'aws_elasticache_cluster': ('Database', 'ElastiCache Cluster'),
    'aws_elasticache_replication_group': ('Database', 'ElastiCache Replication Group'),
    'aws_redshift_cluster': ('Data', 'Redshift Cluster'),
    'aws_glue_job': ('Data', 'Glue Job'),
    'aws_glue_crawler': ('Data', 'Glue Crawler'),
    'aws_kinesis_stream': ('Data', 'Kinesis Data Stream'),
    'aws_kinesis_firehose_delivery_stream': ('Data', 'Kinesis Firehose'),
    'aws_athena_database': ('Data', 'Athena Database'),
    'aws_athena_workgroup': ('Data', 'Athena WorkGroup'),
    'aws_emr_cluster': ('Data', 'EMR Cluster'),

    # Networking & Connectivity
    'aws_route_table': ('Networking', 'Route Table'),
    'aws_route': ('Networking', 'Route'),
    'aws_main_route_table_association': ('Networking', 'Route Table Association'),
    'aws_vpc_endpoint': ('Networking', 'VPC Endpoint'),
    'aws_vpc_endpoint_service': ('Networking', 'VPC Endpoint Service'),
    'aws_vpc_peering_connection': ('Networking', 'VPC Peering'),
    'aws_eip': ('Networking', 'Elastic IP'),
    'aws_nat_gateway': ('Networking', 'NAT Gateway'),
    'aws_vpn_gateway': ('Networking', 'VPN Gateway'),
    'aws_customer_gateway': ('Networking', 'Customer Gateway'),
    'aws_vpn_connection': ('Networking', 'VPN Connection'),
    'aws_network_acl': ('Networking', 'Network ACL'),
    'aws_network_acl_rule': ('Networking', 'Network ACL Rule'),
    'aws_lb_target_group': ('Networking', 'Target Group'),
    'aws_lb_listener': ('Networking', 'Load Balancer Listener'),
    'aws_lb_listener_rule': ('Networking', 'Load Balancer Listener Rule'),
    'aws_route53_zone': ('Networking', 'Route 53 Hosted Zone'),
    'aws_route53_record': ('Networking', 'Route 53 Record'),
    'aws_globalaccelerator_accelerator': ('Networking', 'Global Accelerator'),

    # Identity, Security & Compliance
    'aws_kms_key': ('Security', 'KMS Key'),
    'aws_secretsmanager_secret': ('Security', 'Secrets Manager Secret'),
    'aws_secretsmanager_secret_version': ('Security', 'Secrets Manager Secret Version'),
    'aws_cloudtrail': ('Management', 'CloudTrail'),
    'aws_config_configuration_recorder': ('Management', 'AWS Config'),
    'aws_config_delivery_channel': ('Management', 'AWS Config'),
    'aws_config_configuration_recorder_status': ('Management', 'AWS Config'),
    'aws_guardduty_detector': ('Security', 'GuardDuty Detector'),
    'aws_wafv2_web_acl': ('Security', 'AWS WAFv2 Web ACL'),
    'aws_shield_protection': ('Security', 'AWS Shield Advanced'),
    'aws_cognito_user_pool': ('Security', 'Cognito User Pool'),
    'aws_cognito_identity_pool': ('Security', 'Cognito Identity Pool'),
    'aws_ssoadmin_permission_set': ('Security', 'AWS SSO Permission Set'),

    # Monitoring & Observability
    'aws_cloudwatch_log_group': ('Monitoring', 'CloudWatch Log Group'),
    'aws_cloudwatch_metric_alarm': ('Monitoring', 'CloudWatch Alarm'),
    'aws_cloudwatch_event_rule': ('Monitoring', 'EventBridge Rule'),
    'aws_cloudwatch_event_target': ('Monitoring', 'EventBridge Target'),
    'aws_xray_group': ('Monitoring', 'X-Ray Group'),

    # Application Integration & Messaging
    'aws_sqs_queue': ('Integration', 'SQS Queue'),
    'aws_sqs_queue_policy': ('Integration', 'SQS Queue Policy'),
    'aws_sns_topic': ('Integration', 'SNS Topic'),
    'aws_sns_topic_subscription': ('Integration', 'SNS Subscription'),
    'aws_eventbridge_rule': ('Integration', 'EventBridge Rule'),
    'aws_eventbridge_bus': ('Integration', 'EventBridge Bus'),

    # --- Additional AWS resource mappings (broad coverage) ---
    # Analytics
    'aws_athena': ('Data', 'Athena'),
    'aws_cloudsearch_domain': ('Data', 'CloudSearch'),
    'aws_datazone': ('Data', 'DataZone'),
    'aws_finspace': ('Data', 'FinSpace'),
    'aws_kinesis': ('Data', 'Kinesis'),
    'aws_kinesisanalyticsv2_application': ('Data', 'Managed Service for Apache Flink'),
    'aws_kinesis_video_stream': ('Data', 'Kinesis Video Streams'),
    'aws_opensearch_domain': ('Data', 'OpenSearch Service'),
    'aws_opensearchserverless_collection': ('Data', 'OpenSearch Serverless'),
    'aws_redshiftserverless_namespace': ('Data', 'Redshift Serverless'),
    'aws_cleanrooms': ('Data', 'Clean Rooms'),
    'aws_dataexchange': ('Data', 'Data Exchange'),
    'aws_datapipeline_pipeline': ('Data', 'Data Pipeline'),
    'aws_entityresolution_matching_workflow': ('Data', 'Entity Resolution'),
    'aws_glue': ('Data', 'Glue'),
    'aws_glue_catalog_database': ('Data', 'Glue'),
    'aws_lakeformation_data_lake_settings': ('Data', 'Lake Formation'),
    'aws_msk_cluster': ('Data', 'MSK'),

    # Application Integration
    'aws_sfn_state_machine': ('Integration', 'Step Functions'),
    'aws_appflow_flow': ('Integration', 'AppFlow'),
    'aws_b2bi_profile': ('Integration', 'B2B Data Interchange'),
    'aws_eventbridge_rule': ('Integration', 'EventBridge Rule'),
    'aws_mwaa_environment': ('Integration', 'MWAA'),
    'aws_mq_broker': ('Integration', 'Amazon MQ'),
    'aws_sns': ('Integration', 'SNS'),
    'aws_sns_topic': ('Integration', 'SNS Topic'),
    'aws_sqs': ('Integration', 'SQS'),
    'aws_sqs_queue': ('Integration', 'SQS Queue'),
    'aws_swf_domain': ('Integration', 'SWF'),

    # Blockchain
    'aws_managedblockchain_member': ('Data', 'Managed Blockchain'),

    # Business Applications
    'aws_appfabric': ('Management', 'AppFabric'),
    'aws_chime_voice_connector': ('Integration', 'Chime'),
    'aws_connect_instance': ('Integration', 'Amazon Connect'),
    'aws_pinpoint_app': ('Integration', 'Pinpoint'),
    'aws_ses_domain_identity': ('Integration', 'SES'),
    'aws_workmail_organization': ('Management', 'WorkMail'),

    # Cloud Financial Management
    'aws_billingconductor_billing_group': ('Management', 'Billing Conductor'),
    'aws_budgets_budget': ('Management', 'Budgets'),
    'aws_cur_report_definition': ('Management', 'Cost and Usage Report'),

    # Compute
    'aws_imagebuilder_component': ('Compute', 'EC2 Image Builder'),
    'aws_apprunner_service': ('Compute', 'App Runner'),
    'aws_elastic_beanstalk_environment': ('Compute', 'Elastic Beanstalk'),
    'aws_outposts_outpost': ('Compute', 'Outposts'),

    # Databases
    'aws_keyspaces_keyspace': ('Database', 'Keyspaces'),
    'aws_memorydb_cluster': ('Database', 'MemoryDB'),
    'aws_timestreamwrite_database': ('Database', 'Timestream'),
    'aws_lightsail_database': ('Database', 'Lightsail Managed Databases'),

    # Developer Tools
    'aws_codeartifact_repository': ('Management', 'CodeArtifact'),
    'aws_cloud9_environment_ec2': ('Management', 'Cloud9'),
    'aws_codecatalyst_space': ('Management', 'CodeCatalyst'),

    # Frontend & Mobile
    'aws_amplify_app': ('Compute', 'Amplify'),
    'aws_appsync_graphql_api': ('Integration', 'AppSync'),
    'aws_devicefarm_project': ('Management', 'Device Farm'),
    'aws_location_map': ('Integration', 'Location Service'),

    # IoT
    'aws_iot_topic_rule': ('Integration', 'IoT Core'),
    'aws_iot_thing': ('Integration', 'IoT Core'),
    'aws_iot_policy': ('Integration', 'IoT Core'),
    'aws_iot_certificate': ('Integration', 'IoT Core'),
    'aws_iotevents_input': ('Integration', 'IoT Events'),
    'aws_greengrassv2_component_version': ('Integration', 'IoT Greengrass'),
    'aws_iotsitewise_asset': ('Integration', 'IoT SiteWise'),
    'aws_iottwinmaker_workspace': ('Integration', 'IoT TwinMaker'),
    'aws_iotfleetwise_signal_catalog': ('Integration', 'IoT FleetWise'),

    # Machine Learning & AI
    'aws_bedrock': ('AI/ML', 'Bedrock'),
    'aws_codeguru_reviewer_repository_association': ('AI/ML', 'CodeGuru'),
    'aws_comprehend_document_classifier': ('AI/ML', 'Comprehend'),
    'aws_devopsguru_resource_collection': ('AI/ML', 'DevOps Guru'),
    'aws_forecast_dataset_group': ('AI/ML', 'Forecast'),
    'aws_frauddetector_detector': ('AI/ML', 'Fraud Detector'),
    'aws_kendra_index': ('AI/ML', 'Kendra'),
    'aws_lex_bot': ('AI/ML', 'Lex'),
    'aws_lookoutmetrics_anomaly_detector': ('AI/ML', 'Lookout for Metrics'),
    'aws_personalize_dataset': ('AI/ML', 'Personalize'),
    'aws_sagemaker_domain': ('AI/ML', 'SageMaker'),
    'aws_healthlake_fhir_datastore': ('AI/ML', 'HealthLake'),

    # Management & Governance
    'aws_cloudformation_stack': ('Management', 'CloudFormation'),
    'aws_cloudwatch_dashboard': ('Monitoring', 'CloudWatch'),
    'aws_cloudwatch_log_group': ('Monitoring', 'CloudWatch Log Group'),
    'aws_computeoptimizer_enrollment_status': ('Management', 'Compute Optimizer'),
    'aws_licensemanager_license_configuration': ('Management', 'License Manager'),
    'aws_grafana_workspace': ('Monitoring', 'Managed Grafana'),
    'aws_prometheus_workspace': ('Monitoring', 'Managed Prometheus'),
    'aws_opsworks_stack': ('Management', 'OpsWorks'),
    'aws_proton_environment': ('Management', 'Proton'),
    'aws_chatbot_slack_channel_configuration': ('Management', 'Q Developer (Chatbot)'),
    'aws_servicecatalog_portfolio': ('Management', 'Service Catalog'),
    'aws_ssm_parameter': ('Management', 'Systems Manager'),
    'aws_wellarchitected_workload': ('Management', 'Well-Architected Tool'),

    # Media
    'aws_mediaconnect_flow': ('Integration', 'MediaConnect'),
    'aws_mediaconvert_queue': ('Integration', 'MediaConvert'),
    'aws_medialive_channel': ('Integration', 'MediaLive'),
    'aws_mediapackage_channel': ('Integration', 'MediaPackage'),
    'aws_mediastore_container': ('Integration', 'MediaStore'),
    'aws_mediatailor_vod_configuration': ('Integration', 'MediaTailor'),
    'aws_elastictranscoder_pipeline': ('Integration', 'Elastic Transcoder'),
    'aws_ivs_channel': ('Integration', 'Interactive Video Service'),
    'aws_nimblestudio_studio': ('Integration', 'Nimble Studio'),

    # Migration & Transfer
    'aws_mgn_source_server': ('Management', 'Application Migration Service'),
    'aws_dms_replication_instance': ('Management', 'Database Migration Service'),
    'aws_m2_environment': ('Management', 'Mainframe Modernization'),
    'aws_snowball_job': ('Management', 'Snow Family'),
    'aws_datasync_task': ('Management', 'DataSync'),
    'aws_transfer_server': ('Management', 'Transfer Family'),

    # Networking & Content Delivery
    'aws_ec2_transit_gateway': ('Networking', 'Transit Gateway'),
    'aws_dx_connection': ('Networking', 'Direct Connect'),
    'aws_appmesh_mesh': ('Networking', 'App Mesh'),
    'aws_service_discovery_service': ('Networking', 'Cloud Map'),

    # Security, Identity & Compliance
    'aws_acm_certificate': ('Security', 'Certificate Manager'),
    'aws_auditmanager_account': ('Security', 'Audit Manager'),
    'aws_securityhub_account': ('Security', 'Security Hub'),
    'aws_macie2_account': ('Security', 'Macie'),

    # Storage & Backup
    'aws_backup_vault': ('Storage', 'AWS Backup'),
    'aws_backup_plan': ('Storage', 'AWS Backup'),
}


# Azure provider -> category fallback
AZURE_PROVIDER_CATEGORY: Dict[str, str] = {
    'Microsoft.Compute': 'Compute',
    'Microsoft.ClassicCompute': 'Compute',
    'Microsoft.ContainerService': 'Compute',
    'Microsoft.ContainerInstance': 'Compute',
    'Microsoft.App': 'Compute',  # Container Apps
    'Microsoft.AppPlatform': 'Compute',
    'Microsoft.RedHatOpenShift': 'Compute',
    'Microsoft.DesktopVirtualization': 'Compute',
    'Microsoft.VirtualMachineImages': 'Compute',
    'Microsoft.AVS': 'Compute',
    'Microsoft.Batch': 'Compute',
    'Microsoft.Quantum': 'Compute',

    'Microsoft.Storage': 'Storage',
    'Microsoft.DataLakeStore': 'Storage',
    'Microsoft.NetApp': 'Storage',
    'Microsoft.StorageSync': 'Storage',
    'Microsoft.ElasticSan': 'Storage',
    'Microsoft.StorageActions': 'Storage',

    'Microsoft.Sql': 'Database',
    'Microsoft.DBforPostgreSQL': 'Database',
    'Microsoft.DBforMySQL': 'Database',
    'Microsoft.DBforMariaDB': 'Database',
    'Microsoft.DocumentDB': 'Database',
    'Microsoft.Cache': 'Database',
    'Microsoft.Kusto': 'Data',  # Data Explorer
    'Microsoft.AnalysisServices': 'Data',

    'Microsoft.Network': 'Networking',
    'Microsoft.Cdn': 'Networking',
    'Microsoft.TrafficManager': 'Networking',
    'Microsoft.FrontDoor': 'Networking',

    'Microsoft.KeyVault': 'Security',
    'Microsoft.ManagedIdentity': 'Security',
    'Microsoft.Authorization': 'Security',
    'Microsoft.Security': 'Security',
    'Microsoft.Purview': 'Data',
    'Microsoft.SecurityInsights': 'Security',
    'Microsoft.HardwareSecurityModules': 'Security',
    'Microsoft.ConfidentialLedger': 'Security',
    'Microsoft.Attestation': 'Security',

    'Microsoft.OperationalInsights': 'Monitoring',
    'Microsoft.Insights': 'Monitoring',
    'Microsoft.AlertsManagement': 'Monitoring',

    'Microsoft.ApiManagement': 'Integration',
    'Microsoft.ServiceBus': 'Integration',
    'Microsoft.EventHub': 'Integration',
    'Microsoft.EventGrid': 'Integration',
    'Microsoft.Logic': 'Integration',
    'Microsoft.AppConfiguration': 'Integration',
    'Microsoft.Media': 'Integration',
    'Microsoft.Communication': 'Integration',
    'Microsoft.NotificationHubs': 'Integration',
    'Microsoft.SignalRService': 'Integration',

    'Microsoft.MachineLearningServices': 'AI/ML',
    'Microsoft.CognitiveServices': 'AI/ML',
    'Microsoft.Search': 'AI/ML',
    'Microsoft.BotService': 'AI/ML',
    'Microsoft.HealthBot': 'AI/ML',

    'Microsoft.Resources': 'Management',
    'Microsoft.Automation': 'Management',
    'Microsoft.PolicyInsights': 'Management',
    'Microsoft.Blueprint': 'Management',
    'Microsoft.Advisor': 'Management',
    'Microsoft.CostManagement': 'Management',
    'Microsoft.HybridCompute': 'Management',
    'Microsoft.Kubernetes': 'Management',
    'Microsoft.Migrate': 'Management',
    'Microsoft.RecoveryServices': 'Management',
    'Microsoft.DataMigration': 'Management',
    'Microsoft.DevTestLab': 'Management',
    'Microsoft.DeploymentEnvironments': 'Management',

    'Microsoft.DataFactory': 'Data',
    'Microsoft.Synapse': 'Data',
    'Microsoft.StreamAnalytics': 'Data',
    'Microsoft.Databricks': 'Data',
    'Microsoft.DigitalTwins': 'Integration',
    'Microsoft.IoTCentral': 'Integration',
    'Microsoft.Devices': 'Integration',
    'Microsoft.TimeSeriesInsights': 'Integration',
}


def resolve_service_category(resource_type: str):
    """Resolve a resource type to (category, service_name) with fallbacks.
    1) Exact mapping in SERVICE_MAPPING
    2) Azure provider-based fallback for Microsoft.* resource types
    3) Heuristic for azurerm_* terraform resource types
    """
    if resource_type in SERVICE_MAPPING:
        return SERVICE_MAPPING[resource_type]

    if resource_type.startswith('Microsoft.'):
        parts = resource_type.split('/')
        provider = parts[0]
        category = AZURE_PROVIDER_CATEGORY.get(provider)
        if category:
            service_segment = parts[1] if len(parts) > 1 else provider.split('.')[-1]
            from re import sub
            s1 = sub('(.)([A-Z][a-z]+)', r'\1 \2', service_segment)
            s2 = sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
            human = sub(r'[_\-/]+', ' ', s2).strip().title()
            return (category, human)
        service_segment = parts[1] if len(parts) > 1 else provider.split('.')[-1]
        from re import sub
        s1 = sub('(.)([A-Z][a-z]+)', r'\1 \2', service_segment)
        s2 = sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        human = sub(r'[_\-/]+', ' ', s2).strip().title()
        return ('Azure (Other)', human)

    if resource_type.startswith('azurerm_'):
        rem = resource_type[len('azurerm_'):]
        heuristics = [
            ('Compute', ['vm', 'virtual_machine', 'app_service', 'function', 'aks', 'kubernetes', 'container']),
            ('Storage', ['storage', 'blob', 'file', 'datalake']),
            ('Database', ['sql', 'postgres', 'mysql', 'mariadb', 'cosmos', 'redis', 'synapse', 'data_factory', 'datalake']),
            ('Networking', ['vnet', 'virtual_network', 'subnet', 'nsg', 'network', 'ip', 'gateway', 'express_route', 'frontdoor', 'cdn', 'traffic', 'private_endpoint']),
            ('Security', ['key_vault', 'keyvault', 'identity', 'role', 'security']),
            ('Monitoring', ['insights', 'monitor', 'log_analytics', 'alert']),
            ('Integration', ['service_bus', 'eventhub', 'event_grid', 'logic_app', 'apim', 'api_management']),
            ('AI/ML', ['machine_learning', 'ml', 'cognitive', 'search']),
            ('Management', ['resource_group', 'automation', 'policy', 'blueprint']),
            ('Data', ['data_factory', 'synapse', 'stream_analytics', 'databricks']),
        ]
        from re import sub
        for cat, keys in heuristics:
            if any(k in rem for k in keys):
                s1 = sub('(.)([A-Z][a-z]+)', r'\1 \2', rem)
                s2 = sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
                human = sub(r'[_\-/]+', ' ', s2).strip().title()
                return (cat, human)
        from re import sub
        s1 = sub('(.)([A-Z][a-z]+)', r'\1 \2', rem)
        s2 = sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        human = sub(r'[_\-/]+', ' ', s2).strip().title()
        return ('Azure (Other)', human)

    return None


def get_service_category(resource_type: str):
    return resolve_service_category(resource_type)


def is_azure_resource(resource_type: str) -> bool:
    if resource_type.startswith('aws_'):
        return False
    return (
        resource_type in SERVICE_MAPPING or
        resource_type.startswith('Microsoft.') or
        resource_type.startswith('azurerm_')
    )
