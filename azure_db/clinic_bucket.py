from typing import Dict, List
from botbuilder.schema import ConversationReference
from .initializations import CLINIC_BUCKET_STORAGE


LOCATION_BUCKET_MAP = [
    "Centralized Insurance Team",
    "UT Physicians Family Practice - Bayshore",
    "UT Physicians Family Practice - Bellaire",
    "UT Physicians Multispecialty - Bayshore",
    "UT Physicians Multispecialty - Bellaire",
    "UT Physicians Multispecialty - Cinco Ranch",
    "UT Physicians Multispecialty - Greens",
    "UT Physicians Multispecialty - International District",
    "UT Physicians Multispecialty - Jensen",
    "UT Physicians Multispecialty - Rosenberg",
    "UT Physicians Multispecialty - Sienna",
    "UT Physicians Multispecialty - The Heights",
    "UT Physicians Multispecialty - Victory",
]


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
        inner_buckets = {location: {} for location in locations}
        buckets = dict(buckets=inner_buckets)

    # write user to clinic storage
    temp = buckets.get("buckets")
    chosen = temp.get(chosen_location)
    chosen[conversation.user.id] = conversation
    # erase user from previous storage if one
    if previous_location:
        previous = temp.get(previous_location)
        previous.pop(conversation.user.id, "    ")
    await CLINIC_BUCKET_STORAGE.write(buckets)


async def read_users_in_bucket(index_of_bucket: int) -> dict:
    buckets = await CLINIC_BUCKET_STORAGE.read(["buckets"])
    index = LOCATION_BUCKET_MAP[index_of_bucket]
    buckets: Dict[str, Dict] = buckets.get("buckets")
    return buckets.get(index)
