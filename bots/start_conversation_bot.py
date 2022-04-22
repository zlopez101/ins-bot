from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState
from botbuilder.schema import ChannelAccount, ConversationReference
from helpers.dialog_helper import DialogHelper
from typing import Dict, List


class AlertTeamOfStatusHelp(ActivityHandler):
    def __init__(self, members: Dict[str, ConversationReference]):
        self.members = members

    async def on_turn(self, turn_context: TurnContext):
        return await super().on_turn(turn_context)

    async def on_conversation_update_activity(self, turn_context: TurnContext):
        return await super().on_conversation_update_activity(turn_context)

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        return await super().on_members_added_activity(members_added, turn_context)

