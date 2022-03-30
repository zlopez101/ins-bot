"""Waterfall Dialog to assist with a inquiry with referrals
"""

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


class Referral_Required_Dialog(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accessor: StatePropertyAccessor,
    ):
        super().__init__(
            Referral_Required_Dialog.__name__,
            user_state_accessor,
            conversation_state_accessor,
        )
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, []))

        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Check if insurance requires a referral."

    async def referrals_required(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await self.state_set_up()
