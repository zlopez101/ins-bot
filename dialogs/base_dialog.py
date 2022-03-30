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
from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.schema import SuggestedActions, CardAction, ActionTypes

from aiohttp import ClientSession
from insurance_checker import models, async_api


class BaseDialog(ComponentDialog):
    def __init__(
        self,
        name: str,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):

        super().__init__(name)
        self.session = async_api.Session()
        self.conversation_state_accesor = conversation_state_accesor
        self.user_state_accessor = user_state_accessor

    async def state_set_up(self, step_context: WaterfallStepContext):
        self.conversation_state: models.Conversation_State = await self.conversation_state_accesor.get(
            step_context.context
        )
        self.user_state: models.UserProfile = await self.user_state_accessor.get(
            step_context.context
        )
