from typing import List
from botbuilder.schema import ConversationReference
from .initializations import CLINIC_BUCKET_STORAGE
import os


async def write_user_to_clinic_bucket(
    conversation: ConversationReference,
    chosen_location: str,
    locations: List[str],
    previous_location: str = None,
) -> None:
    """Record the user into a clinic bucket by the conversation reference in order to proactively message when needed

    Args:
        conversation (ConversationReference): The conversation reference to store to the clinic bucket
        chosen_location (str): users's selected clinic location
    """
    # get the storage, read method returns empty dict if keys not found, see documentation
    buckets: dict = await CLINIC_BUCKET_STORAGE.read(["buckets"])
    # first time
    if not buckets:
        # create the Dict[str, Dict]
        # value will be Dict[user_id: conversations]
        buckets = {location: {} for location in locations}
    # write user to clinic storage
    chosen = buckets.get(chosen_location, {})
    chosen[conversation.user.id] = conversation
    # erase user from previous storage if one
    if previous_location:
        previous = buckets.get(previous_location)
        previous.pop(conversation.user.id)
    await CLINIC_BUCKET_STORAGE.write(dict(buckets=buckets))


async def read_users_in_bucket(bucket: str) -> dict:
    buckets = await CLINIC_BUCKET_STORAGE.read(["buckets"])
    return buckets.get("buckets").get(bucket)
