from typing import Union
from datetime import datetime
from .bot import UserProfile
from .api import Insurance, Provider, CPT_code
from dataclasses import dataclass, asdict
from botbuilder.core import StoreItem
from botbuilder.azure import CosmosDbStorage


@dataclass
class _Model(UserProfile):
    time: datetime = datetime.now()
    coverage: Insurance = None

    @classmethod
    def create(cls, user_profile: UserProfile, **kwargs):
        return cls(**asdict(user_profile), **kwargs)


@dataclass
class ProviderNetworkStatus(_Model, UserProfile):
    workflow: str = "Provider Network Status"
    provider: Provider = None


@dataclass
class ReferralRequired(_Model, UserProfile):
    workflow: str = "Referral Required"
    required: bool = False


@dataclass
class VaccineVerification(_Model, UserProfile):
    workflow: str = "Vaccine Verification"
    code: CPT_code = None


@dataclass
class ProcedureVerification(_Model, UserProfile):
    workflow: str = "Vaccine Verification"
    code: CPT_code = None
    provider: Provider = None


class ConversationItem(StoreItem):
    def __init__(
        self,
        conversation: Union[
            ProcedureVerification,
            VaccineVerification,
            ReferralRequired,
            ProviderNetworkStatus,
        ],
    ):
        super().__init__()
        self.conversation = conversation
        self.e_tag = "*"


async def write_conversation_to_storage(
    conversation: Union[
        ProcedureVerification,
        VaccineVerification,
        ReferralRequired,
        ProviderNetworkStatus,
    ],
    storage: CosmosDbStorage,
) -> str:
    """Write the conversation to storage, and return the e_tag attribute as a reference # for the user

    Args:
        item (ConversationItem): Conversation Item to store

    Returns:
        str: e_tag reference #
    """
    await storage.write(conversation)

