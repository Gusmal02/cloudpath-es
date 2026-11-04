export interface CloudService {
  id: string
  label: string
  category: string
  icon: string
  description: string
}

export const cloudServices: Record<string, CloudService[]> = {
  AWS: [
    { id: 'ec2', label: 'EC2', category: 'Cómputo', icon: '🖥️', description: 'Instancias virtuales (IaaS), cómputo bajo demanda' },
    { id: 'lambda', label: 'Lambda', category: 'Cómputo', icon: 'λ', description: 'Funciones serverless, se ejecutan por eventos sin gestionar servidores' },
    { id: 'ecs', label: 'ECS', category: 'Cómputo', icon: '🐳', description: 'Orquestación de contenedores Docker administrada por AWS' },
    { id: 's3', label: 'S3', category: 'Almacenamiento', icon: '🪣', description: 'Almacenamiento de objetos ilimitado, alta durabilidad (11 nueves)' },
    { id: 'ebs', label: 'EBS', category: 'Almacenamiento', icon: '💾', description: 'Volúmenes de bloque para instancias EC2, como disco duro en la nube' },
    { id: 'rds', label: 'RDS', category: 'Base de datos', icon: '🗄️', description: 'Bases de datos relacionales administradas (MySQL, PostgreSQL, etc.)' },
    { id: 'dynamodb', label: 'DynamoDB', category: 'Base de datos', icon: '⚡', description: 'Base de datos NoSQL serverless, latencia en milisegundos' },
    { id: 'elasticache', label: 'ElastiCache', category: 'Base de datos', icon: '🔋', description: 'Caché en memoria (Redis/Memcached), acelera consultas frecuentes' },
    { id: 'vpc', label: 'VPC', category: 'Red', icon: '🔒', description: 'Red privada virtual aislada, controla el tráfico de red' },
    { id: 'elb', label: 'Load Balancer', category: 'Red', icon: '⚖️', description: 'Distribuye el tráfico entre múltiples instancias automáticamente' },
    { id: 'cloudfront', label: 'CloudFront', category: 'Red', icon: '🌐', description: 'CDN global, entrega contenido desde el edge más cercano al usuario' },
    { id: 'route53', label: 'Route 53', category: 'Red', icon: '🗺️', description: 'Servicio DNS administrado con alta disponibilidad' },
    { id: 'iam', label: 'IAM', category: 'Seguridad', icon: '🔑', description: 'Gestión de identidades y permisos, controla quién accede a qué' },
    { id: 'kms', label: 'KMS', category: 'Seguridad', icon: '🔐', description: 'Gestión de claves de cifrado para proteger datos en reposo y tránsito' },
    { id: 'sqs', label: 'SQS (Cola)', category: 'Mensajería', icon: '📨', description: 'Cola de mensajes desacoplada, garantiza entrega sin perder mensajes' },
    { id: 'sns', label: 'SNS (Notif.)', category: 'Mensajería', icon: '📢', description: 'Notificaciones push de uno a muchos (pub/sub), alertas y fanout' },
    { id: 'eventbridge', label: 'EventBridge', category: 'Mensajería', icon: '⚡', description: 'Bus de eventos serverless para integrar servicios con reglas y filtros' },
    { id: 'kinesis', label: 'Kinesis', category: 'Mensajería', icon: '🌊', description: 'Streaming de datos en tiempo real, procesa millones de eventos/seg' },
    { id: 'cloudwatch', label: 'CloudWatch', category: 'Monitoreo', icon: '📊', description: 'Métricas, logs y alertas para todos los servicios AWS' },
    { id: 'cloudtrail', label: 'CloudTrail', category: 'Monitoreo', icon: '🔍', description: 'Auditoría de llamadas a la API, registro de quién hizo qué y cuándo' },
  ],
  GCP: [
    { id: 'gce', label: 'Compute Engine', category: 'Cómputo', icon: '🖥️', description: 'Máquinas virtuales IaaS con múltiples tipos de CPU y GPU' },
    { id: 'gcf', label: 'Cloud Functions', category: 'Cómputo', icon: 'λ', description: 'Funciones serverless, se ejecutan en respuesta a eventos HTTP o GCP' },
    { id: 'gke', label: 'GKE', category: 'Cómputo', icon: '🐳', description: 'Kubernetes administrado por Google, el más maduro del mercado' },
    { id: 'gcs', label: 'Cloud Storage', category: 'Almacenamiento', icon: '🪣', description: 'Almacenamiento de objetos unificado con clases por frecuencia de acceso' },
    { id: 'cloudsql', label: 'Cloud SQL', category: 'Base de datos', icon: '🗄️', description: 'Bases de datos relacionales administradas (MySQL, PostgreSQL, SQL Server)' },
    { id: 'firestore', label: 'Firestore', category: 'Base de datos', icon: '⚡', description: 'Base de datos NoSQL documental serverless, sincronización en tiempo real' },
    { id: 'bigtable', label: 'Bigtable', category: 'Base de datos', icon: '🔋', description: 'Base de datos columnar para analytics y IoT a escala masiva' },
    { id: 'vpc_gcp', label: 'VPC', category: 'Red', icon: '🔒', description: 'Red virtual privada con routing global y segmentación por subredes' },
    { id: 'lb_gcp', label: 'Cloud LB', category: 'Red', icon: '⚖️', description: 'Balanceador de carga global que opera en capa 4 y 7' },
    { id: 'cdn_gcp', label: 'Cloud CDN', category: 'Red', icon: '🌐', description: 'Red de entrega de contenido integrada con Cloud LB para baja latencia' },
    { id: 'iam_gcp', label: 'IAM', category: 'Seguridad', icon: '🔑', description: 'Control de acceso basado en roles para todos los recursos GCP' },
    { id: 'pubsub', label: 'Pub/Sub (Cola)', category: 'Mensajería', icon: '📨', description: 'Mensajería asíncrona pub/sub de alta escala para integración de servicios' },
    { id: 'tasks', label: 'Cloud Tasks', category: 'Mensajería', icon: '📋', description: 'Cola de tareas administrada para ejecución asíncrona con reintentos' },
    { id: 'monitoring', label: 'Cloud Monitoring', category: 'Monitoreo', icon: '📊', description: 'Visibilidad de rendimiento con métricas, paneles y alertas integradas' },
    { id: 'logging', label: 'Cloud Logging', category: 'Monitoreo', icon: '🔍', description: 'Registro centralizado de logs con búsqueda y retención configurable' },
  ],
  AZURE: [
    { id: 'vm', label: 'Virtual Machine', category: 'Cómputo', icon: '🖥️', description: 'Máquinas virtuales IaaS con soporte para Windows y Linux' },
    { id: 'functions', label: 'Azure Functions', category: 'Cómputo', icon: 'λ', description: 'Funciones serverless activadas por eventos HTTP, timer, cola, etc.' },
    { id: 'aks', label: 'AKS', category: 'Cómputo', icon: '🐳', description: 'Kubernetes administrado por Azure con integración al ecosistema Microsoft' },
    { id: 'blob', label: 'Blob Storage', category: 'Almacenamiento', icon: '🪣', description: 'Almacenamiento de objetos no estructurados con niveles Hot/Cool/Archive' },
    { id: 'sqldb', label: 'SQL Database', category: 'Base de datos', icon: '🗄️', description: 'Base de datos relacional PaaS basada en SQL Server totalmente administrada' },
    { id: 'cosmos', label: 'Cosmos DB', category: 'Base de datos', icon: '⚡', description: 'Base de datos NoSQL multimodelo con distribución global y baja latencia' },
    { id: 'redis', label: 'Azure Cache', category: 'Base de datos', icon: '🔋', description: 'Caché en memoria basado en Redis para acelerar aplicaciones' },
    { id: 'vnet', label: 'VNet', category: 'Red', icon: '🔒', description: 'Red virtual aislada que conecta recursos Azure de forma segura' },
    { id: 'lb_az', label: 'Load Balancer', category: 'Red', icon: '⚖️', description: 'Distribución de tráfico en capa 4 con alta disponibilidad' },
    { id: 'cdn_az', label: 'Azure CDN', category: 'Red', icon: '🌐', description: 'Red de entrega de contenido global para reducir latencia de acceso' },
    { id: 'aad', label: 'Azure AD', category: 'Seguridad', icon: '🔑', description: 'Identidad en la nube (IdP) para SSO, MFA y gestión de usuarios' },
    { id: 'keyvault', label: 'Key Vault', category: 'Seguridad', icon: '🔐', description: 'Almacén seguro de secretos, claves y certificados digitales' },
    { id: 'servicebus', label: 'Service Bus (Cola)', category: 'Mensajería', icon: '📨', description: 'Mensajería empresarial con colas y temas para integración de servicios' },
    { id: 'eventhubs', label: 'Event Hubs', category: 'Mensajería', icon: '⚡', description: 'Plataforma de streaming de big data para ingestar millones de eventos/seg' },
    { id: 'eventgrid', label: 'Event Grid', category: 'Mensajería', icon: '🌐', description: 'Enrutamiento de eventos reactivo de uno a muchos con filtros' },
    { id: 'monitor', label: 'Azure Monitor', category: 'Monitoreo', icon: '📊', description: 'Plataforma unificada de observabilidad con métricas, logs y alertas' },
  ],
}
