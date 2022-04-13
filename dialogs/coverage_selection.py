"""Holds class that implements the coverage selection process"""

from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions, TextPrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.choices.list_style import ListStyle

import api
from models.bot import Insurance
from dialogs.base_dialog import BaseDialog


class Coverage_Selection(BaseDialog):
    """Implements the coverage selection process and returns a coverage to be consumed by dialog that called it"""

    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super().__init__(
            Coverage_Selection.__name__, user_state_accessor, conversation_state_accesor
        )

        self.add_dialog(
            WaterfallDialog("OuterDialog", [self.payer_name_step, self.begin_inner],)
        )
        self.add_dialog(
            WaterfallDialog(
                "CoverageSelectionSteps",
                [self.coverages_by_payer, self.confirm_coverage_seletion],
            )
        )
        self.add_dialog(
            WaterfallDialog(
                "PayerSelectionSteps",
                [self.begin_payer_selection, self.confirm_payer_selection],
            )
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = "PayerSelectionSteps"

    async def payer_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Have the user select a payer from a list"""
        await self.state_set_up(step_context)
        async with self.session as session:
            payers = api.coverages.get_payers(session)
            self.payers = await api.coverages.get_payers(session)

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Select a Payer. Click `Next` to show the next 5."
                ),
                choices=[
                    Choice(payer) for payer in [*sorted(self.payers), "None of these"]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def begin_payer_selection(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.options:
            step_context.values.update(step_context.options)
        else:
            async with self.session as session:
                step_context.values["payers"] = await api.coverages.get_payers(session)
                step_context.values["beg"] = 0
                step_context.values["end"] = 5

        payers = sorted(
            step_context.values["payers"][
                step_context.values["beg"] : step_context.values["end"]
            ]
        )

        if not payers:
            await step_context.context.send_activity(
                "that's all the payers, go through the list again"
            )
            step_context.values["beg"] = 0
            step_context.values["end"] = 5
            payers = sorted(
                step_context.values["payers"][
                    step_context.values["beg"] : step_context.values["end"]
                ]
            )

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Select a Payer. If you don't the correct payer, select `next`"
                ),
                choices=[Choice(payer) for payer in [*payers, "Show the next 5"]],
                style=ListStyle.hero_card,
            ),
        )

    async def confirm_payer_selection(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result.value.startswith("Show the next"):
            # await step_context.context.send_activity(MessageFactory.text("Here are the next 5 payers"))
            step_context.values["end"] += 5
            step_context.values["beg"] += 5
            return await step_context.replace_dialog(
                "PayerSelectionSteps", dict(**step_context.values)
            )
        else:
            return await step_context.begin_dialog(
                "CoverageSelectionSteps", dict(payer=step_context.result.value)
            )

    async def begin_inner(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Begin the inner dialog process"""
        return await step_context.begin_dialog(
            "CoverageSelectionSteps", dict(payer=step_context.result.value)
        )

    async def coverages_by_payer(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Have the user select a coverage based on payer selection"""
        step_context.values.update(**step_context.options)
        async with self.session as session:
            coverages, offset = await api.coverages.get_coverages_by_payer_name(
                session,
                step_context.values["payer"],
                offset=step_context.values.get("offset"),
            )
        step_context.values["offset"] = offset
        # b/c sorted will fail if there if coverages was not an iterable
        # TBD -> get_coverages_by_payer_name return a list of 1?

        if len(coverages) > 1:
            coverages = sorted(coverages, key=lambda coverage: coverage.insurance_name)

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"Select the correct coverage associated with payer {step_context.values['payer']}. Select `next` to see the next 5 coverages."
                ),
                choices=[
                    Choice(coverage.insurance_name)
                    for coverage in [
                        *coverages,
                        Insurance(
                            id=0,
                            insurance_name="Next",
                            payer_name="",  # fake information to get the list comphrension to work
                        ),
                    ]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def confirm_coverage_seletion(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Save the coverage before ending the dialog"""
        if step_context.result.value.startswith("Next"):
            await step_context.context.send_activity(
                MessageFactory.text("Show the next 5 coverages")
            )
            return await step_context.replace_dialog(
                "CoverageSelectionSteps", dict(**step_context.values)
            )
        else:
            async with self.session as session:
                coverage, _ = await api.coverages.get_coverage_by_name(
                    session, step_context.result.value
                )
        return await step_context.end_dialog(coverage[0])


class OON_coverages(BaseDialog):
    pass
