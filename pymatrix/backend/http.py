import aiohttp
import asyncio
import pymatrix.backend.backend

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

class HttpBackend(pymatrix.backend.backend.BackendBase):
    """
    A HTTP backend
    """

    _session = None
    _hostname = None
    _port = None

    def __init__(self):
        self._session = None

    def connect(
        self,
        hostname,
        port=pymatrix.backend.backend.DEFAULT_MARIX_PORT):
        """
        Creates a HTTPS session ready to accept messages
        """
        if(self._session is not None):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.disconnect())
            self.hostname = None
            self._port = None

        self._session = aiohttp.ClientSession()
        self._hostname = hostname
        self._port = port

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

        print(message.__dict__)
        response = await self._session.request(
            # proxy="http://localhost:8080",
            # verify_ssl=False,
            method=message.method,
            url="https://{hostname}:{port}{url}".format(
                hostname=self._hostname,
                port=self._port,
                url=message.url),
            json=message.body,
            headers=message.headers
            )
        return response

    async def read_events(self):
        """
        Reads from the backend to receive new events
        """
        pass

class HttpTransportOptions:
    def __init__(self, verb):
        self.verb = verb

def _set_method(method, func):
    def wrapper(*args, **kwargs):
        message = func(*args, **kwargs)
        message.method = method
        message.headers = {"Content-Type": "application/json", "Accept": "*/*"}
        return message
    return wrapper

def delete(func):
    """
    This will set the message as a DELETE message
    """
    return _set_method(_METHOD_DELETE, func)

def get(func):
    """
    This will set the message as a GET message
    """
    return _set_method(_METHOD_GET, func)

def post(func):
    """
    This will set the message as a POST message
    """
    return _set_method(_METHOD_POST, func)

def put(func):
    """
    This will set the message as a PUT message
    """
    return _set_method(_METHOD_PUT, func)
