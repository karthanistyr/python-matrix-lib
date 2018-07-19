import aiohttp
import asyncio
import pymatrix.backend.base

_METHOD_GET="GET"
_METHOD_PUT="PUT"
_METHOD_POST="POST"
_METHOD_DELETE="DELETE"

class HttpBackendError(Exception):
    def __init__(self, message):
        super().__init__(message)

class RestMessage:
    """
    A simple REST message
    """
    method = None
    url = None
    body = None
    headers = None

    def __init__(self, url, method=_METHOD_GET, body=None, headers=None):
        self.method = method
        self.url = url
        self.body = body
        self.headers = headers

class Response:
    def __init__(self, body, is_error):
        self._body = body
        self._is_error = is_error

    @property
    def body(self): return self._body
    @property
    def is_error(self): return self._is_error

class HttpBackend(pymatrix.backend.base.BackendBase):
    """
    A HTTP backend
    """

    _session = None
    _hostname = None
    _port = None

    def __init__(self):
        self._session = None

    async def connect(
        self,
        hostname,
        port):
        """
        Creates a HTTPS session ready to accept messages
        """
        if(self._session is not None):
            await self.disconnect()
            self.hostname = None
            self._port = None

        real_port = port
        if(real_port is None):
            real_port = pymatrix.backend.base.DEFAULT_MARIX_PORT

        self._session = aiohttp.ClientSession()
        self._hostname = hostname
        self._port = real_port

    async def disconnect(self):
        """
        Disconnects from the server and cleans the resources
        """
        await self._session.close()
        self._session = None

    async def write_event(self, message: RestMessage):
        """
        Writes events to the backend to send to the server
        """

        response = await self._session.request(
            # proxy="http://localhost:8080",
            # verify_ssl=False,
            method=message.method,
            url="http://{hostname}:{port}{url}".format(
                hostname=self._hostname,
                port=self._port,
                url=message.url),
            json=message.body,
            headers=message.headers
            )

        return_response = Response(await response.json(),
            True if response.status >= 400 else False)
        return return_response

    async def read_events(self):
        """
        Reads from the backend to receive new events
        """
        pass
