from botbuilder.azure import CosmosDbPartitionedStorage, CosmosDbPartitionedConfig
from config import DefaultConfig

CONFIG = DefaultConfig()
# Create MemoryStorage, UserState and ConversationState
USER_CONFIG = CosmosDbPartitionedConfig(
    container_throughput=0,
    cosmos_db_endpoint=CONFIG.COSMOS_DB_URI,
    auth_key=CONFIG.COSMOS_DB_PRIMARY_KEY,
    database_id=CONFIG.COSMOS_DB_DATABASE_ID,
    container_id=CONFIG.COSMOS_DB_CONTAINER_ID,
    compatibility_mode=False,
)
AZURE_USER_MEMORY = CosmosDbPartitionedStorage(USER_CONFIG)

CONVERSATION_DATA_CONFIG = CosmosDbPartitionedConfig(
    container_throughput=0,
    cosmos_db_endpoint=CONFIG.COSMOS_DB_URI,
    auth_key=CONFIG.COSMOS_DB_PRIMARY_KEY,
    database_id=CONFIG.COSMOS_DB_DATABASE_ID,
    container_id=CONFIG.COSMOS_DB_CONVERSATION_CONTAINER_ID,
    compatibility_mode=False,
)
AZURE_CONVERSATION_MEMORY = CosmosDbPartitionedStorage(CONVERSATION_DATA_CONFIG)

CLINIC_BUCKET_CONFIG = CosmosDbPartitionedConfig(
    container_throughput=0,
    cosmos_db_endpoint=CONFIG.COSMOS_DB_URI,
    auth_key=CONFIG.COSMOS_DB_PRIMARY_KEY,
    database_id=CONFIG.COSMOS_DB_DATABASE_ID,
    container_id=CONFIG.COSMOS_DB_CLINIC_BUCKETS_CONTAINER_ID,
    compatibility_mode=False,
)
CLINIC_BUCKET_STORAGE = CosmosDbPartitionedStorage(CLINIC_BUCKET_CONFIG)
