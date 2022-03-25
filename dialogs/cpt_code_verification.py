# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Text
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
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, ConversationState
from botbuilder.schema import SuggestedActions, CardAction, ActionTypes


from models.state import CodeConversationData


class InsuranceSpecificationDialog(ComponentDialog):
    pass


class CPT_Code_Verification_Dialog(ComponentDialog):
    def __init__(self, conversation_state: ConversationState):
        super(CPT_Code_Verification_Dialog, self).__init__(
            CPT_Code_Verification_Dialog.__name__
        )

        self.conversation_profile_accessor = conversation_state.create_property(
            "code_and_insurance_combination"
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    # self.choices_step,
                    self.cpt_step,
                    self.insurance_step,
                    self.confirmation_step,
                    self.inquiry_results_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    # async def choices_step(
    #     self, step_context: WaterfallStepContext
    # ) -> DialogTurnResult:
    #     return await step_context.prompt(
    #         ChoicePrompt.__name__,
    #         PromptOptions(
    #             prompt=MessageFactory.text("choose something"),
    #             choices=[Choice(v) for v in "abcde"],
    #         ),
    #     )

    async def cpt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """store insurance to check against and prompts user for the CPT code to check

        Args:
            step_context (WaterfallStepContext): incoming step context. need to save the insurance selected to check against

        Returns:
            DialogTurnResult: To be passed to the `age_step` function. 
        """
        # store the name of the insurance here
        # step_context.values["insurance_submitted"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter the cpt code to check")
            ),
        )

    async def insurance_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Begins the step context

        Args:
            step_context (WaterfallStepContext): [description]

        Returns:
            DialogTurnResult: [description]
        """
        # WaterfallStep always finishes with the end of the Waterfall or with another dialog;
        # here it is a Prompt Dialog. Running a prompt here means the next WaterfallStep will
        # be run when the users response is received.
        step_context.values["cpt_code"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter the insurance")),
        )

    # async def age_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
    #     """This is a step that would only be active if the cpt code submitted has an age requirement (HPV, Shingles). Still TBD

    #     Args:
    #         step_context (WaterfallStepContext): incoming step context. need to save to the CPT_code to check

    #     Returns:
    #         DialogTurnResult: To be passed to the `confirmation_step` function. sends user further info regarding cpt code check and awaits their response to age query.
    #     """
    #     pass

    async def confirmation_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """[summary]

        Args:
            step_context (WaterfallStepContext): [description]

        Returns:
            DialogTurnResult: [description]
        """
        step_context.values["insurance_submitted"] = step_context.result

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"You are checking if the code {step_context.values['cpt_code']} is covered by {step_context.values['insurance_submitted']} insurance. Is this correct?"
                )
            ),
        )

    async def inquiry_results_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Display inquiry results for user to take action on

        Args:
            step_context (WaterfallStepContext): Confirmation step_context result. If truthy, run the query and return result. If false, allow user to restart

        Returns:
            DialogTurnResult: results of inquiry
        """
        if step_context.result:
            code_conversation_data = await self.conversation_profile_accessor.get(
                step_context.context, CodeConversationData
            )

            code_conversation_data.cpt_code = step_context.values["cpt_code"]
            code_conversation_data.insurance_submitted = step_context.values[
                "insurance_submitted"
            ]
            # result = perform_insurance_cpt_check(
            #     step_context.values["cpt_code"],
            #     step_context.values["insurance_submitted"],
            # )
            await step_context.context.send_activity(
                MessageFactory.text(
                    # f"The cpt code {result['code']} is {result['covered?']} by the insurance {result['insurance']}.{result.get('explanation', '')} To query another insurance and cpt code combination, send me a message. Thanks!"
                    f"I will check if {code_conversation_data.cpt_code} is covered by {code_conversation_data.insurance_submitted}."
                )
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text("FINE THEN FUCK YOU TOO")
            )
            # await step_context.context.send_activity(
            #     "Sorry getting the wrong information! To try again, please send me any message."
            # )
        return await step_context.end_dialog()

