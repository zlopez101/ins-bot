#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

load_dotenv()
""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    COSMOS_DB_URI = os.environ.get("COSMOS_DB_URI")
    COSMOS_DB_PRIMARY_KEY = os.environ.get("COSMOS_DB_PRIMARY_KEY")
    COSMOS_DB_DATABASE_ID = os.environ.get("COSMOS_DB_DATABASE_ID")
    COSMOS_DB_CONTAINER_ID = os.environ.get("COSMOS_DB_CONTAINER_ID")

