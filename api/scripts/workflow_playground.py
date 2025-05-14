import asyncio
from workflows.base import build_workflow_with_state
from event_handlers import PrintEventHandler
from langchain_core.messages import HumanMessage

from prompts import (
    casual_fan_prompt,
    HumanMessage,
    AIMessage,
)


workflow, state = build_workflow_with_state(
    handler=PrintEventHandler(),
    session_id='5aed14ff09fb415ba77439409f458909',
    messages=[
        HumanMessage(content="tell me about some players in everglade fc"),
    ],
)

async def main():
    await workflow.ainvoke(state)

if __name__ == "__main__":
    asyncio.run(main())
