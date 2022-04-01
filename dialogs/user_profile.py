from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    PromptOptions,
)

from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.dialogs.choices.list_style import ListStyle

from dialogs.base_dialog import BaseDialog
from insurance_checker import async_api, models


class User_Profile_Dialog(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super().__init__(
            User_Profile_Dialog.__name__,
            user_state_accessor,
            conversation_state_accesor,
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.preferred_name_step,
                    self.clinic_step,
                    self.role_step,
                    self.confirm_step,
                    self.save_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Set up user profile"

    async def preferred_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await self.state_set_up(step_context)
        return await step_context.prompt(TextPrompt.__name__, options=PromptOptions(
            prompt=MessageFactory.text('Please enter your preferred first name')
        ))

    async def clinic_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values['name'] = step_context.result
        async with self.session as session:
            locations = await async_api.get_locations(session)

        return await step_context.prompt(ChoicePrompt.__name__, options=PromptOptions(
            prompt=MessageFactory.text("Please Select a location"), choices=[Choice(location) for location in locations],
            style=ListStyle.hero_card
        ))
    async def role_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values['location'] = step_context.result.value
        return await step_context.prompt(ChoicePrompt.__name__, options=PromptOptions(
            prompt=MessageFactory.text("Select a role"),
            choices=[Choice(role) for role in ["Patient Access Representative", "Medical Assistant", "Nurse"]],
            style=ListStyle.hero_card
            )
        )

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values['role'] = step_context.result.value
        return await step_context.prompt(ConfirmPrompt.__name__, options=PromptOptions(
            prompt=MessageFactory.text(f"{step_context.values['name']}, I will save your profile as a {step_context.values['role']} at the primary location of {step_context.values['location']}. Is that correct?")
        ))
    
    async def save_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            print('saving results')
            self.user_state = models.UserProfile(**step_context.values)
            await step_context.context.send_activity(MessageFactory.text('Your information has been saved!'))
        else:
            await step_context.context.send_activity(MessageFactory.text("I didn't save your information. You can set up your user profile at any time!"))
        return await step_context.end_dialog()