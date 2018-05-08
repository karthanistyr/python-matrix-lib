import pymatrix.backend
import pymatrix.backend.http
import pymatrix.serialisation
import pymatrix.constants as consts
import pymatrix.specification.base
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

    async def connect(self, hostname, port=None):
        await self._backend.connect(hostname, port)

    async def generic_call(self, call_endpoint_code, *args, **kwargs):
        request_type, response_type = \
            self._specification.get_message_types(
                call_endpoint_code
                )
        request = request_type(*args, **kwargs)

        login_response = await self._backend.write_event(
            self.format_message(request)
            )
        return self._serialiser.deserialise(await login_response.json(),
            response_type)

    async def login(self, username, password):
        return await self.generic_call(
            pymatrix.constants.EndpointNamesEnum.Login,
            user=username, password=password)

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
            pymatrix.specification.r0.Specification()
            )

    def format_message(self, message):
        url = message.transport_options["http"]["endpoint"]
        method = message.transport_options["http"]["method"]
        return pymatrix.backend.http.RestMessage(
            url=url,
            body=self._serialiser.serialise(message),
            method=method
            )
