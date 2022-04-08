"""Holds class that implements the CPT code check dialog"""

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

from insurance_checker import async_api, checker, models

from dialogs.base_dialog import BaseDialog
from dialogs.coverage_selection import Coverage_Selection


class Vaccine_Verification_Dialog(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super().__init__(
            Vaccine_Verification_Dialog.__name__,
            user_state_accessor,
            conversation_state_accesor,
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.call_coverage_selection,
                    self.cpt_step,
                    self.confirmation_step,
                    self.inquiry_results_step,
                    self.finish_combination
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.add_dialog(
            Coverage_Selection(user_state_accessor, conversation_state_accesor)
        )
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Check if a vaccine is covered in the office"
        self.returns = models.Insurance

    async def call_coverage_selection(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Call the coverage selection dialog to have user select insurance"""

        await self.state_set_up(step_context)
        return await step_context.begin_dialog(Coverage_Selection.__name__)

    async def cpt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Ask for the CPT code to check"""
        step_context.values['coverage'] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter the cpt code to check")
            ),
        )

    async def confirmation_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirms with user that the correct code was selected"""
        async with self.session as session:
            cpt_code, _ = await async_api.get_cpt_code_by_code(
                session, step_context.result
            )
        # if the API call was successful
        if cpt_code:
            self.conversation_state.cpt_code = cpt_code[0]
        
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(
                        f"You are checking if the code {self.conversation_state.cpt_code.name} (CPT {self.conversation_state.cpt_code.code}) is covered by {step_context.values['coverage'].insurance_name}. Is this correct?"
                    )
                ),
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text(
                    f"{step_context.result} code is not found in the database, please try again"
                )
            )
            return await step_context.replace_dialog(WaterfallDialog.__name__)

    async def inquiry_results_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Display inquiry results"""
        if step_context.result:  # the code/insurance combo is correct
            if checker.check_cpt_code_insurance_age_combination(
                self.conversation_state.cpt_code, step_context.values['coverage']
            ):
                await step_context.context.send_activity(
                    MessageFactory.text(
                        # f"The cpt code {result['code']} is {result['covered?']} by the insurance {result['insurance']}.{result.get('explanation', '')} To query another insurance and cpt code combination, send me a message. Thanks!"
                        f"Yes, the vaccine {self.conversation_state.cpt_code.name} (CPT {self.conversation_state.cpt_code.code}) is covered by {step_context.values['coverage'].insurance_name}."
                    )
                )
            else:  # there is some exception
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"The vaccine {self.conversation_state.cpt_code.name} (CPT {self.conversation_state.cpt_code.code}) is **NOT** covered by {step_context.values['coverage'].insurance_name}."
                    )
                )

            # check again
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(
                        "Do you want to lookup if another code is covered?"
                    )
                ),
            )

        else:
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Ok! Would you like to try again?")
                ),
            )

    async def finish_combination(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        if step_context.result:
            return await step_context.begin_dialog(self.initial_dialog_id)
        else:
            return await step_context.end_dialog()
