"""Waterfall Dialog to assist with a inquiry with referrals
"""

from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.dialogs import DialogTurnResult, WaterfallDialog, WaterfallStepContext
import checker
from models.api import Insurance

from dialogs.base_dialog import BaseDialog
from dialogs.coverage_selection import Coverage_Selection


class Referral_Required_Dialog(BaseDialog):
    def __init__(
        self,
        user_state_accessor: StatePropertyAccessor,
        conversation_state_accessor: StatePropertyAccessor,
    ):
        super().__init__(
            Referral_Required_Dialog.__name__,
            user_state_accessor,
            conversation_state_accessor,
        )
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [self.get_coverage, self.referral_required]
            )
        )
        self.add_dialog(
            Coverage_Selection(self.user_state_accessor, conversation_state_accessor)
        )
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Check if insurance requires a referral."
        self.returns = Insurance

    async def get_coverage(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Begin the coverage_selection dialog"""

        await self.state_set_up(step_context)
        return await step_context.begin_dialog(Coverage_Selection.__name__)

    async def referral_required(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Check if the insurance has a referral required flag"""
        coverage = step_context.result
        ref_required = checker.requires_referral(coverage)
        language = "requires" if ref_required else "does not require"
        await step_context.context.send_activity(
            MessageFactory.text(f"{coverage.insurance_name} {language} a referral.")
        )
        return await step_context.end_dialog()

