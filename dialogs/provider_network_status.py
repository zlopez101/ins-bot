"""Determine provider's network status with a plan"""

from email.message import Message
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    PromptOptions,
    ActivityPrompt,
)

from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.schema import SuggestedActions, CardAction, ActionTypes

from dialogs.base_dialog import BaseDialog
from dialogs.coverage_selection import Coverage_Selection

class Provider_Network_Status(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accessor: StatePropertyAccessor,
    ):
        super().__init__(
            Provider_Network_Status.__name__,
            user_state_accessor,
            conversation_state_accessor,
        )
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, []))
        self.add_dialog(Coverage_Selection(self.user_state_accessor, conversation_state_accessor))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Is my provider in-network with patient's insurance?"

    async def get_coverage(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Begin the coverage_selection dialog"""

        await self.state_set_up()
        return await step_context.begin_dialog(Coverage_Selection.__name__)

    async def request_provider(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """"""
        await step_context.context.send_activity(
            MessageFactory.text("Now that we have selected the correct coverage, you'll need to tell me the provider being seen.")
        )

        














    