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
from botbuilder.schema import Activity, ActivityTypes, ConversationReference

# from typing import Dict


from config import DefaultConfig
from bots import DialogBot

from azure_db.initializations import AZURE_USER_MEMORY

from azure_db.clinic_bucket import read_users_in_bucket

CONFIG = DefaultConfig()
# CONVERSATION_REFERENCES: Dict[str, ConversationReference] = dict()
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
    await context.send_activity(
        "If you have the time, please fill out a [bug report](https://insurance-verification.notion.site/Bug-Reports-801d7a667d8542e79a2e077a0c30f8f2). This helps me get better."
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


# in-memory conversation data
MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)

# Create user state based on import
USER_STATE = UserState(AZURE_USER_MEMORY)

# create main dialog and bot
BOT = DialogBot(CONVERSATION_STATE, USER_STATE)

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

routes = web.RouteTableDef()


@routes.get("/notify/{location}")
async def notify(location: str):
    users = await read_users_in_bucket(int(location))
    for reference in users.values():
        await ADAPTER.continue_conversation(
            reference,
            lambda turn_context: turn_context.send_activity("proactive hello"),
            CONFIG.APP_ID,
        )
    return Response(status=HTTPStatus.OK, text="Proactive messages sent!")


APP.add_routes(routes)

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
