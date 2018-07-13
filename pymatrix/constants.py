from enum import Enum
from abc import ABCMeta, abstractmethod

ErrorCodeBase = 1000
class ErrorStringEnum(Enum):
    NoLoginProvided = ErrorCodeBase + 1
    MalformedMessage = ErrorCodeBase + 2
    NotInSpecification = ErrorCodeBase + 3

SpecLevelIndexBase = 0
class SpecLevelEnum(Enum):
    r0 = SpecLevelIndexBase + 1
    r1 = SpecLevelIndexBase + 2

class MatrixMessageType:
    m_login_password = "m.login.password"
    m_login_token = "m.login.token"

EndpointNameIndexBase = 0
class EndpointNamesEnum(Enum):
    # r0 endpoint names; may not be compatible with future spec revisions
    Versions = EndpointNameIndexBase + 1
    Login = EndpointNameIndexBase + 2
    Logout = EndpointNameIndexBase + 3
    Register = EndpointNameIndexBase + 4
    RegisterEmailRequestToken = EndpointNameIndexBase + 5
    AccountPassword = EndpointNameIndexBase + 6
    AccountPasswordRequestToken = EndpointNameIndexBase + 7
    AccountDeactivate = EndpointNameIndexBase + 8
    Account3pid = EndpointNameIndexBase + 9
    Account3pidEmailRequestToken = EndpointNameIndexBase + 10
    AccountWhoami = EndpointNameIndexBase + 11
