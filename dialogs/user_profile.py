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


class User_Profile_Dialog(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super().__init__(
            User_Profile_Dialog.__name__,
            user_state_accessor,
            conversation_state_accesor,
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.preferred_name_step,
                    self.clinic_step,
                    self.role_step,
                    self.save_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Set up user profile"

    async def preferred_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        self.state_set_up()
        pass

    async def clinic_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pass

    async def role_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pass

    async def save_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pass
