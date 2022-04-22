#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

if not os.environ.get("production"):
    PORT = 3978
    from dotenv import load_dotenv

    load_dotenv()
else:
    PORT = 8000

print("")


class DefaultConfig:
    """ Bot Configuration """

    PORT = PORT
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    COSMOS_DB_URI = os.environ.get("COSMOS_DB_URI")
    COSMOS_DB_PRIMARY_KEY = os.environ.get("COSMOS_DB_PRIMARY_KEY")
    COSMOS_DB_DATABASE_ID = os.environ.get("COSMOS_DB_DATABASE_ID")
    COSMOS_DB_CONTAINER_ID = os.environ.get("COSMOS_DB_CONTAINER_ID")
    COSMOS_DB_CONVERSATION_CONTAINER_ID = os.environ.get(
        "COSMOS_DB_CONVERSATION_CONTAINER_ID"
    )
    COSMOS_DB_CLINIC_BUCKETS_CONTAINER_ID = os.environ.get(
        "COSMOS_DB_CLINIC_BUCKETS_CONTAINER_ID"
    )

