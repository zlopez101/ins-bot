from typing import List
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt,
    PromptOptions,
    TextPrompt,
    ConfirmPrompt,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, StatePropertyAccessor

from dialogs.vaccine_verification import Vaccine_Verification_Dialog
from dialogs.referral_required import Referral_Required_Dialog
from dialogs.user_profile import User_Profile_Dialog
from dialogs.base_dialog import BaseDialog
from dialogs.provider_network_status import Provider_Network_Status
from botbuilder.dialogs.choices.list_style import ListStyle

from models import bot


class Workflow:
    def __init__(self, id: int, description: str, dialog_id: str, returns: object):

        self.id = id
        self.description = description
        self.dialog_id = dialog_id
        self.returns = returns

    def __repr__(self):
        return f"Dialog({self.dialog_id}"

    def __eq__(self, __o: object) -> bool:
        if self.id == __o:
            return True
        else:
            return False


class MainDialog(BaseDialog):
    """The Main Dialog"""

    def __init__(self, user_profile_accessor: StatePropertyAccessor):

        super().__init__(MainDialog.__name__, user_profile_accessor)
        self.add_dialog(
            WaterfallDialog(
                "main_loop",
                [self.choose_workflow, self.begin_desired_dialog, self.resume_dialog],
            )
        )
        self.add_dialog(
            WaterfallDialog(
                "signInWaterfall",
                [self.ask_sign_in, self.confirm_sign_in, self.pass_to_workflow],
            )
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_workflows(
            [
                Referral_Required_Dialog,
                Vaccine_Verification_Dialog,
                Provider_Network_Status,
                User_Profile_Dialog,
            ]
        )
        self.initial_dialog_id = "signInWaterfall"

    def add_workflows(self, dialogs: List[ComponentDialog]):
        """This method is called in __init__() and adds the dialogs to the main dialog
        """
        instantiated_dialogs = [
            dialog(self.user_profile_accessor) for dialog in dialogs
        ]
        [self.add_dialog(dialog) for dialog in instantiated_dialogs]
        self.workflows = [
            Workflow(i, dialog.description, dialog.id, dialog.returns)
            for i, dialog in enumerate(instantiated_dialogs)
        ]

    async def ask_sign_in(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """This step will specify the choices that a user interacting with the InsuranceVerification
        bot can make. The user will receive the choices and be prompted to select one. The selected 
        choice will be used by this bot (MainDialog) to begin the correct dialog desired by user.
        """

        self.user_state: bot.UserProfile = await self.user_profile_accessor.get(
            step_context.context, bot.UserProfile
        )
        if not self.user_state.name:
            await step_context.context.send_activity(
                MessageFactory.text("Welcome to the Insurance Verification bot!")
            )
            await step_context.context.send_activity(
                MessageFactory.text(
                    "I can assist with several insurance verification tasks. Before getting started, I'll need some quick information about you to help me answer your inquiries."
                )
            )
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                options=PromptOptions(
                    prompt=MessageFactory.text(
                        "Do you want to sign in? Could be helpful..."
                    )
                ),
            )

        else:
            return await step_context.begin_dialog("main_loop")

    async def confirm_sign_in(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            return await step_context.begin_dialog(self.workflows[-1].dialog_id)
        else:
            return await step_context.begin_dialog("main_loop")

    async def pass_to_workflow(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        return await step_context.begin_dialog("main_loop")

    async def choose_workflow(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # user does want to sign in
        if step_context.result:
            return await step_context.begin_dialog(self.workflows[-1].dialog_id)
        else:
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(
                        f"""Hey {self.user_state.name if self.user_state.name else ''}! I can assist with several workflows and I am adding new features all the time. Please select a workflow to get started!"""
                    ),
                    choices=[
                        Choice(workflow.description) for workflow in self.workflows
                    ],
                    style=ListStyle.hero_card,
                ),
            )

    async def begin_desired_dialog(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if not step_context.result:  # user set up, reprompt for main dialog
            return await step_context.begin_dialog("MainDialog")
        else:  # save the workflow chosen to save the state\
            step_context.values["workflow"] = [
                wq for wq in self.workflows if wq == step_context.result.index
            ][0]

            return await step_context.begin_dialog(
                self.workflows[step_context.result.index].dialog_id
            )

    async def resume_dialog(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        await step_context.context.send_activity(
            MessageFactory.text("To start a new query, send me a message!")
        )
        return await step_context.end_dialog()

