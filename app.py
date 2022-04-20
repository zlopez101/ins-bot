# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    MemoryStorage,
    ConversationState,
    TurnContext,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig
from bots import DialogBot


from botbuilder.azure import CosmosDbPartitionedStorage, CosmosDbPartitionedConfig


CONFIG = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error]: { error }", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity(
        "Yikes! There's been an error with my processing. I'm still learning so how to do this insurance verification stuff!"
    )
    await context.send_activity("To start over, send me a new message.")
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )

        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)

    # Clear out state
    await CONVERSATION_STATE.delete(context)


# Set the error handler on the Adapter.
# In this case, we want an unbound method, so MethodType is not needed.
ADAPTER.on_turn_error = on_error


# Create MemoryStorage, UserState and ConversationState
cosmos_config = CosmosDbPartitionedConfig(
    cosmos_db_endpoint=CONFIG.COSMOS_DB_URI,
    auth_key=CONFIG.COSMOS_DB_PRIMARY_KEY,
    database_id=CONFIG.COSMOS_DB_DATABASE_ID,
    container_id=CONFIG.COSMOS_DB_CONTAINER_ID,
    compatibility_mode=False,
)

workflow_cosmos_config = CosmosDbPartitionedConfig(
    cosmos_db_endpoint=CONFIG.COSMOS_DB_URI,
    auth_key=CONFIG.COSMOS_DB_PRIMARY_KEY,
    database_id=CONFIG.COSMOS_DB_DATABASE_ID,
    container_id=CONFIG.COSMOS_DB_CONVERSATION_CONTAINER_ID,
    compatibility_mode=False,
)

AZURE_CONVERSATION_MEMORY = CosmosDbPartitionedStorage(workflow_cosmos_config)
AZURE_USER_MEMORY = CosmosDbPartitionedStorage(cosmos_config)
# AZURE_USER_STATE = UserState(AZURE_CONVERSATION_MEMORY)

# in-memory conversation data
MEMORY = MemoryStorage()
USER_STATE = UserState(AZURE_USER_MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# create main dialog and bot
BOT = DialogBot(CONVERSATION_STATE, USER_STATE, AZURE_CONVERSATION_MEMORY)


# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""
    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)


async def home_handler(req: Request) -> Response:
    return Response(body="Hello World! Logging configured")


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/", home_handler)


def make_app():
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    APP.router.add_post("/api/messages", messages)
    APP.router.add_get("/", home_handler)
    return APP


def main():
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error


if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
