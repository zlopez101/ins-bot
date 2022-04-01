from typing import List
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions, TextPrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState, ConversationState

from dialogs.vaccine_verification import Vaccine_Verification_Dialog
from dialogs.referral_required import Referral_Required_Dialog
from dialogs.user_profile import User_Profile_Dialog


from botbuilder.dialogs.choices.list_style import ListStyle

from insurance_checker import async_api, models


class Workflow:
    def __init__(self, id: int, description: str, dialog_id: str):

        self.id = id
        self.description = description
        self.dialog_id = dialog_id


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState, conversation_state: ConversationState):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.user_state_accessor = user_state.create_property("User State")
        self.conversation_state_accessor = conversation_state.create_property(
            "Conversation State"
        )
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.choose_a_workflow,
                    self.begin_desired_dialog,
                    self.resume_dialog,
                    self.end_result,
                ],
            )
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_workflows(
            [
                Referral_Required_Dialog,
                Vaccine_Verification_Dialog,
                User_Profile_Dialog,
            ]
        )
        self.initial_dialog_id = WaterfallDialog.__name__
        self.conversation_start = True
        self.session = async_api.Session()

    def add_workflows(self, dialogs: List[ComponentDialog]):
        """This method is called in __init__() and adds the dialogs to the main dialog
        """
        instantiated_dialogs = [
            dialog(self.user_state_accessor, self.conversation_state_accessor)
            for dialog in dialogs
        ]
        [self.add_dialog(dialog) for dialog in instantiated_dialogs]
        self.workflows = [
            Workflow(i, dialog.description, dialog.id)
            for i, dialog in enumerate(instantiated_dialogs)
        ]

    async def choose_a_workflow(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """This step will specify the choices that a user interacting with the InsuranceVerification
        bot can make. The user will receive the choices and be prompted to select one. The selected 
        choice will be used by this bot (MainDialog) to begin the correct dialog desired by user.
        """
        if self.conversation_start:
            self.conversation_state: models.Conversation_State = await self.conversation_state_accessor.get(
                step_context.context, models.Conversation_State
            )

            self.user_state: models.UserProfile = await self.user_state_accessor.get(
                step_context.context, models.UserProfile
            )
            self.conversation_start = False

        print(self.user_state)
        if self.user_state.name:
            print('reading results')

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    """Welcome to the Insurance Verification bot! I can assist with several workflows and I am adding new features all the time. Please select a workflow to get started!"""
                ),
                choices=[Choice(workflow.description) for workflow in self.workflows],
                style=ListStyle.hero_card,
            ),
        )

    async def begin_desired_dialog(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["workflow_desired"] = step_context.result.value
        index = [wf.description for wf in self.workflows].index(
            step_context.result.value
        )

        await step_context.context.send_activity(
            MessageFactory.text(
                f"you chose to {step_context.result.value.lower()}. Good Luck!"
            )
        )

        return await step_context.begin_dialog(self.workflows[index].dialog_id)

    async def resume_dialog(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        print(self.user_state)

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Hopefully I answered your questions! You can either:"
                ),
                choices=[
                    Choice(value="Continue with this patient"),
                    Choice(value="Choose a new patient"),
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def end_result(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()
