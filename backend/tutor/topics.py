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
        "exam_domains": [
            "Cloud Concepts",
            "Data and Storage",
            "Compute",
            "Networking",
            "Security and Compliance",
        ],
        "key_services": [
            "Compute Engine", "Cloud Storage", "BigQuery", "Cloud SQL",
            "Cloud Functions", "GKE", "Pub/Sub", "Cloud CDN",
            "Cloud IAM", "VPC", "Cloud Monitoring", "Cloud Logging",
        ],
    },
    "AZURE": {
        "name": "Microsoft Azure Fundamentals (AZ-900)",
        "exam_domains": [
            "Cloud Concepts",
            "Azure Core Services",
            "Security and Compliance",
            "Pricing and Support",
        ],
        "key_services": [
            "Virtual Machines", "Blob Storage", "Azure SQL Database",
            "Azure Functions", "Azure Kubernetes Service", "Azure CDN",
            "Azure Active Directory", "Virtual Network", "Azure Monitor",
            "Service Bus", "Cosmos DB", "Azure DevOps",
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
