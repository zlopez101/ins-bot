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


class User_Profile_Dialog(ComponentDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super(User_Profile_Dialog, self).__init__(User_Profile_Dialog.__name__)

        self.conversation_state_accesor = conversation_state_accesor
        self.user_state_accessor = user_state_accessor
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, []))

        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Set up user profile"

    async def preferred_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        pass

    async def clinic_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pass

    async def role_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pass
