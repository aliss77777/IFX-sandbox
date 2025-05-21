import asyncio
from utils.zep_helpers import ZepClient

zep_client = ZepClient()
user_id = 'huge@hugeinc.com'

session_id = zep_client\
    .get_or_create_user(user_id, "Hugh", "Bigly") \
    .create_session() \
    .session_id
print(session_id)

async def main():
    memory = await zep_client.get_memory_async(session_id)
    print(f'Memory: {memory}')
    print(memory.context)

if __name__ == "__main__":
    asyncio.run(main())
