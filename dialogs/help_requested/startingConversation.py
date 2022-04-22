from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallStepContext,
    WaterfallDialog,
    DialogTurnResult,
)


class Start(ComponentDialog):
    def __init__(self):
        super().__init__(self.__name__)
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__), [self.start])

    async def start(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity(
            "An insurance verification task has been requested at your clinic"
        )
        return await step_context.end_dialog()
