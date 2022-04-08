"""Holds the property accessor factory functions for memory storage. All attributes for these types of class should be initialized to zero"""


from insurance_checker import models
from dataclasses import dataclass
from enum import Enum


class Workflow(Enum):
    """Holds all the workflows """
    ProcedureVerification = 0
    VaccineVerification = 1
    ReferralRequired = 2
    ProviderNetworkStatus = 3
    UserProfileSetUp = 4


@dataclass
class CoverageSelection:

    coverage: models.Insurance = None

class UserFeedBack:

    user_rating: bool = None
    user_feedback: str = None

@dataclass
class ProcedureVerification(CoverageSelection, UserFeedBack):

    procedure_code: int = None
    diagnosis_code: str = None
    rendering_provider: models.Provider = None

@dataclass
class VaccineVerification(CoverageSelection, UserFeedBack):

    procedure_code: int = None

@dataclass
class ProviderNetworkStatus(CoverageSelection, UserFeedBack):

    requesting_provider: models.Provider = None


@dataclass
class UserProfile(UserFeedBack):
    """used to save user profile information"""
    name: str = None
    role: str = None
    location: str = None

class Workflow(Enum):
    """Holds all the workflows """
    ProcedureVerification = ProcedureVerification
    VaccineVerification = 1
    ReferralRequired = 2
    ProviderNetworkStatus = 3
    UserProfileSetUp = UserProfile


@dataclass
class ConversationState:
    """To be used for in-memory storage"""
    workflow: str
    


@dataclass
class SaveConversationState(ConversationState):
    """Used to save the conversation state into the Azure Cosmos DB"""
    pass


if __name__ == '__main__':
    pc = ProcedureVerification()