"""Holds class that implements the coverage selection process"""

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
)
from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions, TextPrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.choices.list_style import ListStyle
from insurance_checker import async_api, models

from dialogs.base_dialog import BaseDialog


class Coverage_Selection(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super().__init__(
            Coverage_Selection.__name__, user_state_accessor, conversation_state_accesor
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [self.payer_name_step, self.coverages_by_payer, self.save_coverages],
            )
        )

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def payer_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Have the user select a payer from a list"""
        await self.state_set_up(step_context)
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
        # TBD -> get_coverages_by_payer_name return a list of 1?
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

    async def save_coverages(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Save the coverage before ending the dialog"""
        async with self.session as session:
            self.conversation_state.coverage = await async_api.get_coverage_by_name(
                session, step_context.result.value
            )
        print(self.conversation_state)
        return await step_context.end_dialog()

