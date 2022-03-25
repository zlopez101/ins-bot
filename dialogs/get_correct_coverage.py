"""Waterfall Dialog to confirm the correct patient coverage option
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
from aiohttp import ClientSession

from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState
from botbuilder.schema import SuggestedActions, CardAction, ActionTypes

from insurance_checker import async_api


class Get_Correct_Coverage(ComponentDialog):
    def __init__(self):  # not sure why user state is needed
        super(Get_Correct_Coverage, self).__init__(Get_Correct_Coverage)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, []))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def payer_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Have the user select a payer from a list

        Args:
            step_context (WaterfallStepContext): Step Context object. Used for saving information

        Returns:
            DialogTurnResult: 
        """
        self.session = ClientSession()
        self.payers = await async_api.get_payers(self.session)
        return step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Select a Payer"),
                choices=[Choice(payer) for payer in self.payers],
            ),
        )

    async def coverages_by_payer(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """The user selected a coverage

        Args:
            step_context (WaterfallStepContext): _description_

        Returns:
            DialogTurnResult: _description_
        """
        step_context.values["payer_selected"] = step_context.result.value
        coverages = await async_api.get_coverages_by_payer_name(
            self.session, step_context.result.value
        )
        return step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"Select a coverage associated with payer {step_context.values['payer_selected']} "
                ),
                choices=[Choice(coverage.insurance_name) for coverage in coverages],
            ),
        )

