from abc import ABCMeta, abstractmethod

DEFAULT_MARIX_PORT=8448

class BackendBase(metaclass=ABCMeta):
    """
    Base class for a client-server backend. Backends may include
    HTTP/S, TCP sockets...
    """

    @abstractmethod
    def connect(
        self,
        hostname,
        port
        ):
        """
        Connects to the server
        """
        pass

    @abstractmethod
    async def disconnect(self):
        """
        Disconnects from the server and cleans the resources
        """
        pass

    @abstractmethod
    async def write_event(self, message):
        """
        Writes events to the backend to send to the server
        """
        pass

    @abstractmethod
    async def read_events(self):
        """
        Reads from the backend to receive new events
        """
        pass
