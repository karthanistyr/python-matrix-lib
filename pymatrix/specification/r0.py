import pymatrix.constants
import pymatrix.error
import pymatrix.localisation
import pymatrix.serialisation
import inspect

class RequestMessageBase:
    def __init__(self, type, transport_options=None):
        self._type = type
        self._transport_options = transport_options

    @pymatrix.serialisation.serialisable
    def type(self):
        return self._type

class LoginRequestMessage(RequestMessageBase):
    def __init__(
        self,
        user=None,
        address=None,
        password=None,
        token=None,
        device_id=None,
        initial_device_display_name=None
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
            type = pymatrix.constants.MessageType.m_login_password
            if(address is not None):
                medium = "email"
        elif (token is not None
            and user is None
            and address is None
            and password is None):
            type = pymatrix.constants.MessageType.m_login_token
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

        super().__init__(type)

    @pymatrix.serialisation.serialisable
    def user(self):
        return self._user
    @pymatrix.serialisation.serialisable
    def address(self):
        return self._address
    @pymatrix.serialisation.serialisable
    def medium(self):
        return self._medium
    @pymatrix.serialisation.serialisable
    def password(self):
        return self._password
    @pymatrix.serialisation.serialisable
    def token(self):
        return self._token
    @pymatrix.serialisation.serialisable
    def device_id(self):
        return self._device_id
    @pymatrix.serialisation.serialisable
    def initial_device_display_name(self):
        return self._initial_device_display_name

class Specification:

    endpoints = {
        pymatrix.constants.EndpointNamesEnum.Versions:
            "/_matrix/client/versions",
        pymatrix.constants.EndpointNamesEnum.Login:
            "/_matrix/client/r0/login"
        }

    message_code_type = {
        "login": LoginRequestMessage
    }

    def construct(self, message_code, **kwargs):
        impl_type = self.message_code_type.get(message_code, None)
        if(impl_type is None):
            raise pymatrix.error.SpecificationError(
                pymatrix.localisation.Localisation.get_message(
                    pymatrix.constants.ErrorStringEnum.NoSuchMessageKnown
                )
            )
        return impl_type(**kwargs)
