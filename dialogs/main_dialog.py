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

from dialogs.cpt_code_verification import CPT_Code_Verification_Dialog
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
                    self.payer_name_step,
                    self.coverages_by_payer,
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
                CPT_Code_Verification_Dialog,
                User_Profile_Dialog,
            ]
        )
        self.initial_dialog_id = WaterfallDialog.__name__
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

    async def payer_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Have the user select a payer from a list"""
        async with self.session as session:
            self.payers = await async_api.get_payers(session)

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Select a Payer. If you don't see your payer selected `None of these`"
                ),
                choices=[
                    Choice(payer) for payer in [*sorted(self.payers), "None of these"]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def coverages_by_payer(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Have the user select a coverage based on payer selection"""
        step_context.values["payer_selected"] = step_context.result.value
        async with self.session as session:
            coverages = await async_api.get_coverages_by_payer_name(
                session, step_context.values["payer_selected"]
            )
        # b/c sorted will fail if there if coverages was not an iterable
        if len(coverages) > 1:
            coverages = sorted(coverages)

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"Select a coverage associated with payer {step_context.values['payer_selected']}. If you don't see your payer selected `None of these`"
                ),
                choices=[
                    Choice(coverage.insurance_name)
                    for coverage in [
                        *coverages,
                        models.Insurance(
                            id=0,
                            insurance_name="None of these",
                            payer_name="",  # fake information to get the list comphrension to work
                        ),
                    ]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def choose_a_workflow(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """This step will specify the choices that a user interacting with the InsuranceVerification
        bot can make. The user will receive the choices and be prompted to select one. The selected 
        choice will be used by this bot (MainDialog) to begin the correct dialog desired by user.
        """
        step_context.values["coverage_selected"] = step_context.result.value
        conversation_state = await self.conversation_state_accessor.get(
            step_context.context, models.Conversation_State
        )
        async with self.session as session:
            conversation_state.coverage = await async_api.get_coverage_by_name(
                session, step_context.values["coverage_selected"]
            )
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    """Thanks for confirming the visit coverage! I can help with these workflows:"""
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
