"""Determine provider's network status with a plan"""

from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.core import MessageFactory, StatePropertyAccessor

from dialogs.base_dialog import BaseDialog
from dialogs.coverage_selection import Coverage_Selection
from dialogs.provider_selection import Provider_Selection

from models.dialog import ProviderNetworkStatus


class Provider_Network_Status(BaseDialog):
    def __init__(self, user_profile_accessor: StatePropertyAccessor):
        super().__init__(Provider_Network_Status.__name__, user_profile_accessor)
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [self.get_coverage, self.get_provider, self.check_network_status],
            )
        )
        self.add_dialog(Coverage_Selection(self.user_profile_accessor))
        self.add_dialog(Provider_Selection(user_profile_accessor))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Is my provider in-network with patient's insurance?"
        self.returns = None

    async def get_coverage(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Begin the coverage_selection dialog"""

        await self.state_set_up(step_context)
        return await step_context.begin_dialog(Coverage_Selection.__name__)

    async def get_provider(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["coverage"] = step_context.result
        return await step_context.begin_dialog(Provider_Selection.__name__)

    async def check_network_status(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await step_context.context.send_activity(
            MessageFactory.text(
                f"This is where we check the provider {step_context.result}'s status with the plan {step_context.values['coverage']}."
            )
        )
        result = Provider_Network_Status.create(self.user_state, **step_context.values)
        return await step_context.end_dialog(result)

