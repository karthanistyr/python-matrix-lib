import pymatrix.injection as inject
import asyncio
from enum import Enum

class Client:
    """
    A matrix client
    """
    def __init__(self, api):
        self._api = api

    async def connect(self, hostname, port=None):
        return await self._api.connect(hostname, port)

    async def login(self, username, password):
        return await self._api.login(username, password)

    async def logout(self):
        await self._api.logout()

class ClientFactory:

    def get_client(api=None):
        api_instance = api \
            if api is not None \
            else inject.get_instance(inject.DEFAULT_API_TYPE)
        return Client(api_instance)
