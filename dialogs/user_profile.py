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

from models.bot import ChoiceLooper, UserProfile
import api


class User_Profile_Dialog(BaseDialog):
    def __init__(self, user_profile_accessor: StatePropertyAccessor):
        super().__init__(User_Profile_Dialog.__name__, user_profile_accessor)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.preferred_name_step,
                    self.clinic_step,
                    self.role_step,
                    self.confirm_step,
                    self.save_step,
                ],
            )
        )
        self.add_dialog(
            WaterfallDialog(
                "LocationSelectionDialog", [self.choose_location, self.confirm_location]
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Set up user profile"
        self.help_url = "https://insurance-verification.notion.site/User-Profile-25a207315ee846089c9aca424d7758f2"

    async def preferred_name_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await self.state_set_up(step_context)
        return await step_context.prompt(
            TextPrompt.__name__,
            options=PromptOptions(
                prompt=MessageFactory.text(
                    "Please enter your name as LAST NAME, FIRST NAME format."
                )
            ),
        )

    async def clinic_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        last, first = step_context.result.split(",")
        step_context.values["last"] = last.strip()
        step_context.values["first"] = first.strip()
        return await step_context.begin_dialog(
            "LocationSelectionDialog", step_context.values
        )

    async def choose_location(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if not step_context.options.get("choices"):
            async with self.session as session:
                locations = await api.providers.get_locations(session)
                self.looping = ChoiceLooper(
                    locations, lambda location: location.split("-")
                )
        step_context.values["choices"] = True

        return await step_context.prompt(
            ChoicePrompt.__name__,
            options=PromptOptions(
                prompt=MessageFactory.text("Please Select a location"),
                choices=[
                    Choice(location) for location in [*next(self.looping), "See Next 5"]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def confirm_location(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result.value.startswith("See"):
            return await step_context.replace_dialog(
                "LocationSelectionDialog", step_context.values
            )
        else:
            return await step_context.end_dialog(step_context.result.value)

    async def role_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["location"] = step_context.result
        return await step_context.prompt(
            ChoicePrompt.__name__,
            options=PromptOptions(
                prompt=MessageFactory.text("Select a role"),
                choices=[
                    Choice(role)
                    for role in [
                        "Patient Access Representative",
                        "Medical Assistant",
                        "Nurse",
                    ]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["role"] = step_context.result.value
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            options=PromptOptions(
                prompt=MessageFactory.text(
                    f"{step_context.values['first']} {step_context.values['last']}, I will save your profile as a {step_context.values['role']} at the primary location of {step_context.values['location']}. Is that correct?"
                )
            ),
        )

    async def save_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            await self.user_profile_accessor.set(
                step_context.context, UserProfile(**step_context.values)
            )
            await step_context.context.send_activity(
                MessageFactory.text("Your information has been saved!")
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "I didn't save your information. You can set up your user profile at any time!"
                )
            )
        return await step_context.end_dialog()
