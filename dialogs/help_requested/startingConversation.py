from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallStepContext,
    WaterfallDialog,
    DialogTurnResult,
)
from botbuilder.core import StatePropertyAccessor


class Start(ComponentDialog):
    def __init__(self, user_profile_accessor: StatePropertyAccessor):
        super().__init__(self.__name__)
        self.user_profile_accessor = user_profile_accessor
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__), [self.start])

    async def start(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity(
            "An insurance verification task has been requested at your clinic"
        )
        return await step_context.end_dialog()
