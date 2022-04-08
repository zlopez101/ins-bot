"""This module contains the BaseDialog Class. All Dialogs, except the MainDialog, will inherit from it.

    * Standardizes the conversation and user state accessors
    * creates a async_api.Session object for API calls
    * defines the state_set_up() method that uses the state accessors to get the state

"""
from botbuilder.dialogs import ComponentDialog, WaterfallStepContext
from botbuilder.core import StatePropertyAccessor


from insurance_checker import models, async_api


class BaseDialog(ComponentDialog):
    def __init__(
        self,
        name: str,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accesor: StatePropertyAccessor,
    ):

        super().__init__(name)
        self.name = name
        self.session = async_api.Session()
        self.conversation_state_accessor = conversation_state_accesor
        self.user_state_accessor = user_state_accessor

    async def state_set_up(self, step_context: WaterfallStepContext):
        self.conversation_state: models.Conversation_State = await self.conversation_state_accessor.get(
            step_context.context
        )
        self.user_state: models.UserProfile = await self.user_state_accessor.get(
            step_context.context
        )

    async def customer_looper():
        pass

    async def custom_begin_dialog(self, dialog_id: str, step_context: WaterfallStepContext):
        return await super().begin_dialog(dialog_id, step_context.values)
