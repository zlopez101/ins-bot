from models.dialog import (
    ProcedureVerification,
    VaccineVerification,
    ReferralRequired,
    ProviderNetworkStatus,
)
from typing import Union
from .initializations import AZURE_CONVERSATION_MEMORY


async def write_conversation_to_storage(
    conversation: Union[
        ProcedureVerification,
        VaccineVerification,
        ReferralRequired,
        ProviderNetworkStatus,
    ],
) -> int:
    """Write the conversation to storage, and return the e_tag attribute as a reference # for the user

    Args:
        item (ConversationItem): Conversation Item to store

    Returns:
        int: hash of workflow, time, and user name
    """
    initials = conversation.first[0] + conversation.last[0]

    storage_id = "@".join([initials, conversation.time.strftime("%y%j%H%M"),])
    await AZURE_CONVERSATION_MEMORY.write({storage_id: conversation.to_dict()})
    return storage_id
