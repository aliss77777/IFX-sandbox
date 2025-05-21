import asyncio
from workflows.base import build_workflow_with_state
from event_handlers import PrintEventHandler
from langchain_core.messages import HumanMessage
from utils.freeplay_helpers import FreeplayClient
from utils.zep_helpers import ZepClient

from prompts import (
    casual_fan_prompt,
    HumanMessage,
    AIMessage,
)
user_id = "huge@hugeinc.com"


# workflow, state = build_workflow_with_state(
#     handler=PrintEventHandler(),
#     session_id='5aed14ff09fb415ba77439409f458909',
#     messages=[
#         HumanMessage(content="tell me about some players in everglade fc"),
#     ],
# )

zep_session_id = ZepClient() \
                .get_or_create_user(user_id, "Hugh", "Bigly") \
                .create_session() \
                .session_id
freeplay_session_id = FreeplayClient().create_session().session_id

workflow_bundle, state = build_workflow_with_state(
    handler=PrintEventHandler(),
    zep_session_id=zep_session_id,
    freeplay_session_id=freeplay_session_id,
    email=user_id,
    first_name="Hugh",
    last_name="Bigly",
    persona="Casual Fan",
    messages=[
        HumanMessage(content="tell me about some players in everglade fc"),
        # HumanMessage(content="tell me about the league")
    ],
)

async def main():
    await workflow_bundle.workflow.ainvoke(state)

if __name__ == "__main__":
    asyncio.run(main())
