import os
from botbuilder.core import BotFrameworkAdapter
from aiohttp.web import Request, Response
from azure_db.clinic_bucket import read_users_in_bucket
from http import HTTPStatus

async def notify(adapter:BotFrameworkAdapter, request: Request, app_id: str):
    users = await read_users_in_bucket(int(request.match_info["location"]))
    if not os.environ.get('production'):
        users = [user for user in users.values()]
    else:
        users = [user for user in users.values() if user['channel_id'] != "emulator"]
    for reference in users:
        await adapter.continue_conversation(
            reference,
            lambda turn_context: turn_context.send_activity("proactive hello"),
            app_id
        )
    return Response(status=HTTPStatus.OK, text="Proactive messages sent!")
