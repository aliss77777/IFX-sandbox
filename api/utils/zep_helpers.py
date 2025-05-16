from functools import lru_cache
from langchain_core.messages import BaseMessage
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message


# @lru_cache(maxsize=1)
def get_zep_client():
    return AsyncZep()


async def record_session(session_id: str, messages: list[BaseMessage]):
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
    zep_client = get_zep_client()
    await zep_client.memory.add(session_id=session_id, messages=messages)
    