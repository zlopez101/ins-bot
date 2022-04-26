"""This module holds the Procedure_Verification_Dialog class."""
from multiprocessing.sharedctypes import Value
import string
from typing import List
from botbuilder.dialogs import (
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
import checker

from dialogs.base_dialog import BaseDialog
from dialogs.coverage_selection import Coverage_Selection
from models.api import CPT_code
import api


class Procedure_Verification_Dialog(BaseDialog):
    """Implements the Procedure Verification Workflow"""

    def __init__(self, user_profile_accessor: StatePropertyAccessor):
        super().__init__(Procedure_Verification_Dialog.__name__, user_profile_accessor)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.call_coverage_selection,
                    self.cpt_step,
                    self.confirmation_step,
                    self.inquiry_results_step,
                ],
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.add_dialog(Coverage_Selection(user_profile_accessor))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Check if a procedure is covered in the office"
        self.help_url = "https://insurance-verification.notion.site/Is-the-procedure-covered-by-insurance-0e8141473bd44ce7ba27432f09766628"

    async def call_coverage_selection(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Call the coverage selection dialog to have user select insurance"""
        return await step_context.begin_dialog(Coverage_Selection.__name__)

    async def cpt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Ask for Procedure code to check"""
        step_context.values["coverage"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Please enter the procedure code(s) to check. If entering multiple codes, please separate codes with a comma."
                )
            ),
        )

    async def confirmation_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirms with user that the correct code was selected"""
        codes = validate_procedure_code(step_context.result)
        if codes:
            async with self.session as session:
                api_codes: List[CPT_code] = []
                for code in codes:
                    result, _ = await api.codes.get_cpt_code_by_code(session, code)
                    api_codes.append(result[0])
            if len(api_codes) > 1:
                msg = f"You are checking if the procedure codes {', '.join([code.code for code in api_codes])} are covered by {step_context.values['coverage'].insurance_name}. Is this correct?"
            else:
                msg = f"You are checking if the procedure code {api_codes[0].code} is covered by {step_context.values['coverage'].insurance_name}. Is this correct?"
            step_context.values["api_codes"] = api_codes
            return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg)),
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text(
                    f'Your codes "{step_context.result} were formatted incorrectly. Please enter as a comma separated list'
                )
            )
            await step_context.replace_dialog(WaterfallDialog.__name__)

    async def inquiry_results_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Display inquiry results"""
        if step_context.result:  # the code/insurance combo is correct
            for code in step_context.values["api_codes"]:
                if checker.check_cpt_code_insurance_age_combination(
                    code, step_context.values["coverage"]
                ):
                    await step_context.context.send_activity(
                        MessageFactory.text(
                            # f"The cpt code {result['code']} is {result['covered?']} by the insurance {result['insurance']}.{result.get('explanation', '')} To query another insurance and cpt code combination, send me a message. Thanks!"
                            f"Yes, the procedure {code.name} (CPT {code.code}) is covered by {step_context.values['coverage'].insurance_name}."
                        )
                    )
                else:  # there is some exception
                    await step_context.context.send_activity(
                        MessageFactory.text(
                            f"No, the procedure {code.name} (CPT {code.code}) is **NOT** covered by {step_context.values['coverage'].insurance_name}."
                        )
                    )
        return await step_context.end_dialog()


def validate_procedure_code(raw_codes_entered: str) -> List[str]:
    """Validate each code entered

    Args:
        raw_codes_entered (str): should be a string of comma separated codes

    Returns:
        List[str]: Procedure codes list
    """
    try:
        return [int(code) for code in raw_codes_entered.split(",")]
    except ValueError:
        return None

