import pymatrix.constants
import pymatrix.error
import pymatrix.localisation
import pymatrix.serialisation
import pymatrix.specification.base
import inspect

endpoints = {
    pymatrix.constants.EndpointNamesEnum.Versions:
        "/_matrix/client/versions",
    pymatrix.constants.EndpointNamesEnum.Login:
        "/_matrix/client/r0/login"
    }

class LoginRequestMessage(pymatrix.specification.base.RequestMessageBase):
    def __init__(self, user=None, address=None, password=None,
        token=None, device_id=None, initial_device_display_name=None
        ):

        # the api allows logging on using a Matrix ID, an email or a token
        if(user is None and address is None and token is None):
            raise pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.NoLoginProvided
                )
            )

        medium = None
        # try to determine type
        if(((user is None) != (address is None))
            and password is not None
            and token is None):
            type = pymatrix.constants.MatrixMessageType.m_login_password
            if(address is not None):
                medium = "email"
        elif (token is not None
            and user is None
            and address is None
            and password is None):
            type = pymatrix.constants.MatrixMessageType.m_login_token
        else:
            raise pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.MalformedMessage
                )
            )

        self._user = user
        self._address = address
        self._medium = medium
        self._password = password
        self._token = token
        self._device_id = device_id
        self._initial_device_display_name = initial_device_display_name

        super().__init__(type,
            {
                "http":
                {
                    "endpoint":
                        endpoints[pymatrix.constants.EndpointNamesEnum.Login],
                    "method":
                        "POST"
                    }
                }
        )

    @pymatrix.serialisation.serialisable
    def user(self): return self._user

    @pymatrix.serialisation.serialisable
    def address(self): return self._address

    @pymatrix.serialisation.serialisable
    def medium(self): return self._medium

    @pymatrix.serialisation.serialisable
    def password(self): return self._password

    @pymatrix.serialisation.serialisable
    def token(self): return self._token

    @pymatrix.serialisation.serialisable
    def device_id(self): return self._device_id

    @pymatrix.serialisation.serialisable
    def initial_device_display_name(self):
        return self._initial_device_display_name

class LoginResponseMessage:

    @pymatrix.serialisation.serialisable
    def user_id(self): return self._user_id
    @user_id.setter
    def user_id(self, value): self._user_id = value

    @pymatrix.serialisation.serialisable
    def access_token(self): return self._access_token
    @access_token.setter
    def access_token(self, value): self._access_token = value

    @pymatrix.serialisation.serialisable
    def home_server(self): return self._home_server
    @home_server.setter
    def home_server(self, value): self._home_server = value

    @pymatrix.serialisation.serialisable
    def device_id(self): return self._device_id
    @device_id.setter
    def device_id(self, value): self._device_id = value


class Specification(pymatrix.specification.base.SpecificationBase):

    message_code_type = {
        pymatrix.constants.EndpointNamesEnum.Login:
            (LoginRequestMessage, LoginResponseMessage, pymatrix.specification.base.ErrorMessageBase)
    }
