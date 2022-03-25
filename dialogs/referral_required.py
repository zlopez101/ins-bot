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
from botbuilder.core import MessageFactory, UserState
from botbuilder.schema import SuggestedActions, CardAction, ActionTypes


class Referral_Required_Dialog(ComponentDialog):
    def __init__(self, user_state: UserState):  # not sure why user state is needed
        super(Referral_Required_Dialog, self).__init__(Referral_Required_Dialog)

        self.user_profile_accessor = user_state.create_property(
            "UserProfile"
        )  # or this line

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, []))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def payer_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        pass
