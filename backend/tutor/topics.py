"""
Registro de certificaciones soportadas por el tutor.
Para añadir una certificación nueva, solo modifica CERTIFICATIONS.
El resto del tutor se adapta automáticamente.
"""

CERTIFICATIONS: dict[str, dict] = {
    "AWS": {
        "name": "AWS Cloud Practitioner (CLF-C02)",
        "exam_domains": [
            "Cloud Concepts",
            "Security and Compliance",
            "Cloud Technology and Services",
            "Billing, Pricing and Support",
        ],
        "key_services": [
            "EC2", "S3", "RDS", "Lambda", "IAM", "VPC", "CloudFront",
            "ECS", "DynamoDB", "SQS", "SNS", "CloudWatch", "Route 53",
            "Elastic Load Balancing", "Auto Scaling", "CloudTrail",
        ],
    },
    "GCP": {
        "name": "Google Cloud Digital Leader",
        # Official blueprint: https://cloud.google.com/learn/certification/guides/cloud-digital-leader
        "exam_domains": [
            "Digital Transformation with Google Cloud",
            "Innovating with Data and Google Cloud",
            "Infrastructure and Application Modernization",
            "Google Cloud Security and Operations",
            "Scaling with Google Cloud Operations",
        ],
        "key_services": [
            "Compute Engine", "Cloud Storage", "BigQuery", "Cloud SQL",
            "Cloud Functions", "GKE", "Pub/Sub", "Cloud CDN",
            "Cloud IAM", "VPC", "Cloud Monitoring", "Cloud Logging",
            "Looker", "Vertex AI", "Cloud Spanner", "Cloud Run",
        ],
    },
    "AZURE": {
        "name": "Microsoft Azure Fundamentals (AZ-900)",
        # Official blueprint: https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/
        "exam_domains": [
            "Cloud Concepts",
            "Azure Architecture and Services",
            "Azure Management and Governance",
        ],
        "key_services": [
            "Virtual Machines", "Blob Storage", "Azure SQL Database",
            "Azure Functions", "Azure Kubernetes Service", "Azure CDN",
            "Microsoft Entra ID", "Virtual Network", "Azure Monitor",
            "Service Bus", "Cosmos DB", "Azure DevOps",
            "Azure Resource Manager", "Azure Policy", "Cost Management",
        ],
    },
}

ALLOWED_TOPICS = {
    "cloud computing", "certificaciones cloud", "aws", "gcp", "azure",
    "google cloud", "microsoft azure", "amazon web services",
    "servicios cloud", "arquitectura cloud", "seguridad cloud",
    "precios cloud", "facturación", "redes", "almacenamiento",
    "cómputo", "bases de datos", "serverless", "contenedores",
    "kubernetes", "docker", "devops", "infraestructura",
}
