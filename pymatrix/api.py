import pymatrix.backend
import pymatrix.backend.http
import pymatrix.serialisation
import pymatrix.specification.interface
import pymatrix.constants as consts
from abc import ABCMeta, abstractmethod

class ApiBase(metaclass=ABCMeta):
    """
    Base class for an API specification. It is an association of a
    backend, a message format, etc...
    """
    def __init__(self, backend, serialiser, specification):
        self._backend = backend
        self._serialiser = serialiser
        self._specification = specification

    async def login(
        self,
        hostname,
        username,
        password,
        port=None
        ):
        self._backend.connect(hostname, port)

        login_response = await self._backend.write_event(
            self.format_message(
                self._specification.get_endpoint(consts.EndpointNamesEnum.Login),
                self._serialiser.serialise(
                    self._specification.get_message(
                        "login",
                        user=username,
                        password=password
                        )
                    )
                )
            )
        return login_response

    async def logout(self):
        await self._backend.disconnect()

    @abstractmethod
    def format_message(url, body):
        pass

class RestApi(ApiBase):
    """
    An API over HTTP/S
    """
    def __init__(self):
        super().__init__(
            pymatrix.backend.http.HttpBackend(),
            pymatrix.serialisation.JsonSerialiser(),
            pymatrix.specification.interface.MessageBroker(
                pymatrix.constants.SpecLevelEnum.r0
                )
            )

    def format_message(self, url, body):
        return pymatrix.backend.http.RestMessage(
            url=url,
            body=body,
            method="POST"
            )
