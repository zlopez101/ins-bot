from typing import Dict
from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState
from botbuilder.core.teams import TeamsActivityHandler
from helpers.dialog_helper import DialogHelper
from botbuilder.core.channel_service_handler import ChannelAccount
from dialogs import main_dialog
from botbuilder.schema import ChannelAccount, ConversationReference, Activity


class TeamsBot(TeamsActivityHandler):
    pass


class DialogBot(ActivityHandler):
    """
    This Bot implementation can run any type of Dialog. The use of type parameterization is to allows multiple
    different bots to be run at different endpoints within the same project. This can be achieved by defining distinct
    Controller types each with dependency on distinct Bot types. The ConversationState is used by the Dialog system. The
    UserState isn't, however, it might have been used in a Dialog implementation, and the requirement is that all
    BotState objects are saved at the end of a turn.
    """

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        # conversation_reference: Dict[str, ConversationReference],
    ):
        if conversation_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. user_state is required but None was given"
            )
        # self.conversation_reference = conversation_reference
        self.conversation_state = conversation_state
        self.user_state = user_state

        self.user_profile_accessor = self.user_state.create_property("User Profile")
        self.dialog = main_dialog.MainDialog(self.user_profile_accessor)

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        # self._add_conversation_reference(turn_context.activity)
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )

    async def on_end_of_conversation_activity(self, turn_context: TurnContext):
        print("end of conversation")
        return await super().on_end_of_conversation_activity(turn_context)

    # def _add_conversation_reference(self, activity: Activity):
    #     """
    #     This populates the shared Dictionary that holds conversation references. In this sample,
    #     this dictionary is used to send a message to members when /api/notify is hit.
    #     :param activity:
    #     :return:
    #     """
    #     conversation_reference = TurnContext.get_conversation_reference(activity)
    #     self.conversation_reference[
    #         conversation_reference.user.id
    #     ] = conversation_reference

    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await DialogHelper.run_dialog(
                    self.dialog,
                    turn_context,
                    self.conversation_state.create_property("DialogState"),
                )
