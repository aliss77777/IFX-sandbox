import uuid
from functools import lru_cache
from langchain_core.messages import BaseMessage
from zep_cloud.client import AsyncZep, Zep
from zep_cloud.types import Message
from zep_cloud.errors import NotFoundError
from typing import Optional


# @lru_cache(maxsize=1)
def _get_zep_client():
    return AsyncZep()


class ZepClient:

    def __init__(self):
        self.zep_client_async = AsyncZep()
        self.zep_client = Zep()
        self._user = None
        self.session_id = None

    async def get_memory_async(self, session_id: Optional[str] = None):
        session_id = session_id or self.session_id
        if session_id is None:
            raise ValueError("No session ID provided")
        return await self.zep_client_async.memory.get(session_id=session_id)

    # async def get_session(self, session_id: str):
    #     return await self.zep_client.session.get(session_id=session_id)

    # async def get_or_create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
    #     if self._user and self._user.user_id == email:
    #         return self
    #     try:
    #         self._user = await self.get_user(email)
    #     except NotFoundError:
    #         self._user = await self.create_user(email, first_name, last_name)
    #     return self

    def get_or_create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
        if self._user and self._user.user_id == email:
            return self
        try:
            self.get_user(email)
        except NotFoundError:
            self.create_user(email, first_name, last_name)
        return self

    def create_session(self):
        session_id = uuid.uuid4().hex # A new session identifier
        self.zep_client.memory.add_session(
            session_id=session_id,
            user_id=self._user.user_id,
        )
        self.session_id = session_id
        return self

    def create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
        self._user = self.zep_client.user.add(
            user_id=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        return self

    # async def create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
    #     self._user = await self.zep_client.user.add(
    #         user_id=email,
    #         email=email,
    #         first_name=first_name,
    #         last_name=last_name,
    #     )
    #     return self._user

    # async def get_user(self, email: str):
    #     self._user = await self.zep_client.user.get(user_id=email)
    #     return self._user

    def get_user(self, email: str):
        self._user = self.zep_client.user.get(user_id=email)
        return self

    @staticmethod
    def get_zep_client() -> AsyncZep:
        return _get_zep_client()

    async def record_session(self,
                             messages: list[BaseMessage],
                             session_id: Optional[str] = None):
        session_id = session_id or self.session_id
        if session_id is None:
            raise ValueError("No session ID provided")
        if len(messages) >= 2:
            user_message = messages[0]
            assistant_message = messages[-1]
            messages = [
                Message(
                    role="user",
                content=user_message.content,
                role_type="user",
            ),
            Message(
                role="assistant",
                content=assistant_message.content,
                role_type="assistant",
            ),
        ]
        await self.zep_client_async.memory.add(session_id=session_id, messages=messages)


# async def record_session(session_id: str,
#                          messages: list[BaseMessage],
#                          zep_client: AsyncZep = None):
#     if len(messages) >= 2:
#         user_message = messages[0]
#         assistant_message = messages[-1]
#         messages = [
#             Message(
#                 role="user",
#             content=user_message.content,
#             role_type="user",
#         ),
#         Message(
#             role="assistant",
#             content=assistant_message.content,
#             role_type="assistant",
#         ),
#     ]
#     zep_client = zep_client or get_zep_client()
#     await zep_client.memory.add(session_id=session_id, messages=messages)
    