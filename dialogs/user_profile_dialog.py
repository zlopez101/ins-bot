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
    ActivityPrompt,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState
from botbuilder.schema import SuggestedActions, CardAction, ActionTypes

from data_models import UserProfile, perform_insurance_cpt_check
from data_models.models import CptCode

from errors import NotValidInput


class InsuranceSpecificationDialog(ComponentDialog):
    pass


class InsuranceDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(InsuranceDialog, self).__init__(InsuranceDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserProfile")

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

    async def choices_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        reply = MessageFactory.text(
            "Hey! I help automate insurance verification requests. Send me a message to get started!"
        )
        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Red",
                    type=ActionTypes.im_back,
                    value="Red",
                    image="https://via.placeholder.com/20/FF0000?text=R",
                    image_alt_text="R",
                ),
                CardAction(
                    title="Yellow",
                    type=ActionTypes.im_back,
                    value="Yellow",
                    image="https://via.placeholder.com/20/FFFF00?text=Y",
                    image_alt_text="Y",
                ),
                CardAction(
                    title="Blue",
                    type=ActionTypes.im_back,
                    value="Blue",
                    image="https://via.placeholder.com/20/0000FF?text=B",
                    image_alt_text="B",
                ),
            ]
        )
        return await step_context.prompt(reply)

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
        # be run when the users response is received./
        # print(step_context.values)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter the insurance")),
        )

    async def insurance_step_confirmation(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """If a user enters BCBS -> there are multiple BCBS insurances. Have the user select from the dropdown

        **************TBD*****************************

        Args:
            step_context (WaterfallStepContext): [description]

        Returns:
            DialogTurnResult: [description]
        """
        step_context.values["payer_name_submitted"] = step_context.result.value
        pass

    async def cpt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """store insurance to check against and prompts user for the CPT code to check

        Args:
            step_context (WaterfallStepContext): incoming step context. need to save the insurance selected to check against

        Returns:
            DialogTurnResult: To be passed to the `age_step` function. 
        """
        # store the name of the insurance here
        # step_context.values["insurance_submitted"] = step_context.result
        print(step_context.values)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter the cpt code to check")
            ),
        )

    async def age_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """This is a step that would only be active if the cpt code submitted has an age requirement (HPV, Shingles). Still TBD

        Args:
            step_context (WaterfallStepContext): incoming step context. need to save to the CPT_code to check

        Returns:
            DialogTurnResult: To be passed to the `confirmation_step` function. sends user further info regarding cpt code check and awaits their response to age query.
        """
        pass

    async def confirmation_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """[summary]

        Args:
            step_context (WaterfallStepContext): [description]

        Returns:
            DialogTurnResult: [description]
        """
        try:
            step_context.values["cpt_code"] = CptCode.from_user_request(
                step_context.result
            )
        except NotValidInput:
            pass

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"You are checking if {step_context.values['cpt_code'].name.capitalize()} cpt code {step_context.values['cpt_code'].cpt_code} is covered with the {step_context.values['insurance_submitted']} insurance. Is this correct?"
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
            result = perform_insurance_cpt_check(
                step_context.values["cpt_code"],
                step_context.values["insurance_submitted"],
            )
            await step_context.context.send_activity(
                MessageFactory.text(
                    f"The cpt code {result['code']} is {result['covered?']} by the insurance {result['insurance']}.{result.get('explanation', '')} To query another insurance and cpt code combination, send me a message. Thanks!"
                )
            )
        else:
            await step_context.context.send_activity(
                "Sorry getting the wrong information! To try again, please send me any message."
            )
        return await step_context.end_dialog()

