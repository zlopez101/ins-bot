import os

settings = {
    "host": os.environ.get("INS_BOT_DB_HOST"),
    "master_key": os.environ.get("INS_BOT_DB_ACCOUNT_KEY"),
    "database_id": "insurance",
}
