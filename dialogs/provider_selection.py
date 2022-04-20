"""Holds class that implements the provider selection process. Provider_Selection returns a models.Provider as a result"""

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

from dialogs.base_dialog import BaseDialog


class Provider_Selection(BaseDialog):
    """Provider Selection Dialog. Returns a provider object to the calling Dialog"""

    def __init__(self, user_profile_accessor: StatePropertyAccessor):
        super().__init__(Provider_Selection.__name__, user_profile_accessor)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [self.location_selection, self.provider_selection, self.finish],
            )
        )

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.help_url = "https://insurance-verification.notion.site/Provider-Selection-f6367f9df53a44dea0375f38df5402a1"

    async def location_selection(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await self.state_set_up(step_context)
        async with self.session as session:
            locations = await api.providers.get_locations(session)
        return await step_context.prompt(
            ChoicePrompt.__name__,
            options=PromptOptions(
                MessageFactory.text("Select the location"),
                choices=[Choice(location) for location in locations],
                style=ListStyle.hero_card,
            ),
        )

    async def provider_selection(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        async with self.session as session:
            (
                step_context.values["providers"],
                step_context.values["offset"],
            ) = await api.providers.get_providers_at_location(
                session, step_context.result.value
            )
        return await step_context.prompt(
            ChoicePrompt.__name__,
            options=PromptOptions(
                MessageFactory.text("Choose the provider"),
                choices=[
                    Choice(provider.Provider)
                    for provider in step_context.values["providers"]
                ],
                style=ListStyle.hero_card,
            ),
        )

    async def finish(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog(
            step_context.values["providers"][step_context.result.index]
        )

