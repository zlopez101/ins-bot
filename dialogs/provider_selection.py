"""Holds class that implements the provider selection process"""

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
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions, TextPrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.choices.list_style import ListStyle
from insurance_checker import async_api, models

from dialogs.base_dialog import BaseDialog


class Provider_Selection(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):
        super().__init__(
            Provider_Selection.__name__, user_state_accessor, conversation_state_accesor
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [],
            )
        )

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__