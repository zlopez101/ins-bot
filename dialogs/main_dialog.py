from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from dialogs.get_correct_coverage import Get_Correct_Coverage


class Workflow:
    def __init__(self, id: int, description: str, dialog: ComponentDialog):

        self.id = id
        self.description = description
        self.dialog = dialog


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__(self, MainDialog.__name__)
        self.user_state = user_state
        self.workflows = [
            Workflow(1, "Get Coverages associated with payer"),
            (2, "Check if insurance requires a referral."),
            (3, "Check if a CPT code is covered and/or needs authorization"),
            (4, "Display relevant coverages for a given payer"),
        ]
        self.add_dialog(Get_Correct_Coverage())
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, []))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def choose_a_workflow(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """This step will specify the choices that a user interacting with the InsuranceVerification
        bot can make. The user will receive the choices and be prompted to select one. The selected 
        choice will be used by this bot (MainDialog) to begin the correct dialog desired by user.

        Args:
            step_context (WaterfallStepContext)

        Returns:
            DialogTurnResult
        """
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Select a Workflow"),
                choices=[Choice(v) for v in self.workflows],
            ),
        )

    async def begin_desired_dialog(self, step_context: WaterfallStepContext):
        return await step_context.begin_dialog()
