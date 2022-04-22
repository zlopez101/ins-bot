"""This module contains the BaseDialog Class. All Dialogs, except the MainDialog, will inherit from it.

    * Standardizes the conversation and user state accessors
    * creates a api.utils.Session object for API calls
    * defines the state_set_up() method that uses the state accessors to get the state

"""
from email.message import Message
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallStepContext,
    WaterfallDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
    NumberPrompt,
    PromptOptions,
    TextPrompt,
)
from botbuilder.core import StatePropertyAccessor, MessageFactory
from botbuilder.schema import ActivityTypes, InputHints
from models.bot import UserProfile
import api


class BaseDialog(ComponentDialog):
    """Base Dialog class that implements common"""

    def __init__(self, name: str, user_profile_accessor: StatePropertyAccessor):

        super().__init__(name)
        self.name = name
        self.session = api.utils.Session()
        self.user_profile_accessor = user_profile_accessor
        self.help_url = ""
        self.add_dialog(GetInfo(user_profile_accessor))

    async def on_begin_dialog(
        self, inner_dc: DialogContext, options: object
    ) -> DialogTurnResult:
        """Create the user state upon initiaion of the dialog"""
        self.user_state: UserProfile = await self.user_profile_accessor.get(
            inner_dc.context
        )
        return await super().on_begin_dialog(inner_dc, options)

    async def state_set_up(self, step_context: WaterfallStepContext):

        self.user_state: UserProfile = await self.user_profile_accessor.get(
            step_context.context
        )

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result
        return await super().on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()

            # help message block
            if self.help_url:
                help_message_text = f"[Click Here]({self.help_url}) for the help sheet. It can explain how complete this workflow. Thank you!"
            else:
                help_message_text = f"A tip sheet hasn't been created for this workflow. Please send an email to CIT (attn: Zach) to request one. Thank you!"
            append = " Send me any message to continue the dialog."
            help_message = MessageFactory.text(
                help_message_text + append,
                help_message_text + append,
                InputHints.expecting_input,
            )
            if text in ("help", "?"):
                await inner_dc.context.send_activity(help_message)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            # cancel message block
            cancel_message_text = (
                f"Cancelling. Send me any message to start at beginning!"
            )
            cancel_message = MessageFactory.text(
                cancel_message_text, cancel_message_text, InputHints.ignoring_input
            )
            if text in ("cancel", "quit"):
                await inner_dc.context.send_activity(cancel_message)
                return await inner_dc.cancel_all_dialogs()

            # handoff to human block

            if text in ("agent"):
                await inner_dc.context.send_activity("Help is right around the corner!")
                await inner_dc.begin_dialog(GetInfo.__name__)

        return None


class GetInfo(ComponentDialog):
    def __init__(self, user_profile_accessor: StatePropertyAccessor):
        super().__init__(GetInfo.__name__)
        self.session = api.utils.Session()
        self.user_profile_accessor = user_profile_accessor
        self.add_dialog(WaterfallDialog("mrn", [self.get_mrn, self.message, self.end]))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = "mrn"

    async def get_mrn(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.user_state: UserProfile = await self.user_profile_accessor.get(
            step_context.context
        )
        return await step_context.prompt(
            NumberPrompt.__name__,
            options=PromptOptions(MessageFactory.text("Please attach the MRN")),
        )

    async def message(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["mrn"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            options=PromptOptions(
                MessageFactory.text(
                    "Please send a short message to pass along to the team"
                )
            ),
        )

    async def end(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        handoff_message = "Getting someone from the CIT that can help!"
        await step_context.context.send_activity(handoff_message)
        async with self.session as session:
            params = {
                "requestor": f"{self.user_state.first} {self.user_state.last}",
                "mrn": str(step_context.values["mrn"]),
                "location": self.user_state.location,
                "message": step_context.result,
            }
            await session.get(
                f"https://ut-ins-bot-web-app.azurewebsites.net/notify/0", params=params,
            )
        return await step_context.end_dialog()
