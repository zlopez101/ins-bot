"""Waterfall Dialog to assist with a inquiry with referrals
"""
from botbuilder.core import MessageFactory, StatePropertyAccessor
from botbuilder.dialogs import DialogTurnResult, WaterfallDialog, WaterfallStepContext
import checker
from models.api import Insurance

from dialogs.base_dialog import BaseDialog
from dialogs.coverage_selection import Coverage_Selection
from models.bot import UserProfile
from models.dialog import ReferralRequired


class Referral_Required_Dialog(BaseDialog):
    def __init__(
        self, user_profile_accessor: StatePropertyAccessor,
    ):
        super().__init__(Referral_Required_Dialog.__name__, user_profile_accessor)
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [self.get_coverage, self.referral_required]
            )
        )
        self.add_dialog(Coverage_Selection(self.user_profile_accessor))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.description = "Check if insurance requires a referral."
        self.help_url = "https://insurance-verification.notion.site/Are-referrals-required-88bd0dcea65a4b998a1d71b8fd03ae6c"

    async def get_coverage(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Begin the coverage_selection dialog"""

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
        result = ReferralRequired.create(
            self.user_state, coverage=coverage, required=ref_required
        )
        return await step_context.end_dialog(result)

