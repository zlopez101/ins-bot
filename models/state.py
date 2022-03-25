from dataclasses import dataclass
from unicodedata import name


@dataclass
class UserProfile:

    name: str = None
    role: str = None
    location: str = None


@dataclass
class CodeConversationData:

    cpt_code: int = None
    insurance_submitted: str = None
