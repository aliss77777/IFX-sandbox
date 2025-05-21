import asyncio
import datetime
import operator
import time
from dataclasses import dataclass
from typing import Any, Tuple, List, Optional
from functools import partial
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph, END
from langchain_core.callbacks import AsyncCallbackHandler
from langgraph.prebuilt import ToolNode

from utils.freeplay_helpers import FreeplayClient
from utils.zep_helpers import ZepClient 
from prompts import (
    casual_fan_prompt,
)
from tools import (
    Document,
    PlayerSearchTool,
    GameSearchTool,
)


available_tools = [
    GameSearchTool(),
    PlayerSearchTool(),
]
tool_node = ToolNode(available_tools)

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools=available_tools)


class AgentState(TypedDict):
    email: str
    first_name: str
    last_name: str
    zep_session_id: str
    freeplay_session_id: str
    persona: str
    start_time: float
    zep_memory: Optional[str] = None
    messages: Annotated[Sequence[BaseMessage], operator.add]


async def call_model(state: AgentState,
                     handler: AsyncCallbackHandler,
                     zep_client: ZepClient,
                     freeplay_client: FreeplayClient) -> dict:
    zep_session_id = state["zep_session_id"]
    messages = state["messages"]
    persona = state["persona"]
    
    memory = state["zep_memory"]
    if memory is None:
        memory = await zep_client.get_memory_async(session_id=zep_session_id)
        memory = memory.context or "New user/session. No memory."
    
    # old_prompt = casual_fan_prompt.format(
    #     zep_context=memory,
    #     input=messages,
    #     now=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
    # )
    prompt = freeplay_client.get_prompt_by_persona(
        persona=persona,
        variables={
            "now": datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
            "zep_context": memory,
        },
        history=messages,
    )

    # response = await llm_with_tools.ainvoke(prompt, stream=True,
    #                                     config={"callbacks" :[handler]})
    response = await llm_with_tools.with_config(callbacks=[handler]).ainvoke(prompt.llm_prompt, stream=True)

    return {'messages': [response], 'zep_memory': memory}


async def call_tool(state: AgentState,
                    handler: AsyncCallbackHandler) -> dict:
    messages = state["messages"]
    last_message = messages[-1]
    tools_by_name = {tool.name: tool for tool in available_tools}

    observations = []
    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observations.append(
            tool.with_config(callbacks=[handler]).ainvoke(tool_call["args"])
        )

    # await all observations
    observations = await asyncio.gather(*observations)

    results = []
    for observation, tool_call in zip(observations, last_message.tool_calls):
        if isinstance(observation, list) and len(observation) > 0 and isinstance(observation[0], Document):
            observation = "\n\n".join(doc.page_content for doc in observation)
        results.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": results}


async def should_continue(state: AgentState,
                          handler: AsyncCallbackHandler,
                          zep_client: ZepClient,
                          freeplay_client: FreeplayClient) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if 'tool_calls' not in last_message.additional_kwargs:
        # inform zep of final response
        await zep_client.record_session(
            session_id=state["zep_session_id"],
            messages=messages,
        )
        # inform freeplay of final response
        # TODO: wait for feedback from freeplay about tool messages
        # freeplay_client.record_session(state)
        # trigger on_workflow_end callback
        if hasattr(handler, 'on_workflow_end'):
            await handler.on_workflow_end(state)
        return 'end'
    return 'continue'

### WorkflowBundle ###
@dataclass
class WorkflowBundle:
    """
    Bundle containing the compiled workflow and its core dependencies.

    Attributes:
        workflow: The compiled workflow object ready for execution.
        zep_client: The Zep client instance used for memory/context.
        freeplay_client: The Freeplay client instance for session tracking.
    """
    workflow: Any
    zep_client: ZepClient
    freeplay_client: FreeplayClient


def build_workflow(handler: AsyncCallbackHandler) -> WorkflowBundle:
    """
    Build and compile the workflow, returning all core dependencies as a WorkflowBundle.

    Args:
        handler: AsyncCallbackHandler for this workflow.

    Returns:
        WorkflowBundle: Contains compiled workflow, zep_client, and freeplay_client.

    Example usage:
        bundle = build_workflow(handler)
        # Access workflow: bundle.workflow
        # Access zep client: bundle.zep_client
        # Access freeplay client: bundle.freeplay_client
    """
    workflow = StateGraph(AgentState)
    zep_client = ZepClient()
    freeplay_client = FreeplayClient()
    workflow.add_node('agent', partial(call_model, handler=handler, zep_client=zep_client, freeplay_client=freeplay_client))
    workflow.add_node('tools', partial(call_tool, handler=handler))
    workflow.set_entry_point('agent')

    workflow.add_conditional_edges(
        'agent',
        partial(should_continue, handler=handler, zep_client=zep_client, freeplay_client=freeplay_client),
        {
            'continue': 'tools',
            'end': END,
        }
    )

    workflow.add_edge('tools', 'agent')

    return WorkflowBundle(workflow=workflow.compile(), zep_client=zep_client, freeplay_client=freeplay_client)


def build_workflow_with_state(handler: AsyncCallbackHandler,
                              zep_session_id: Optional[str] = None,
                              freeplay_session_id: Optional[str] = None,
                              email: Optional[str] = None,
                              first_name: Optional[str] = None,
                              last_name: Optional[str] = None,
                              persona: Optional[str] = None,
                              messages: Optional[List[BaseMessage]] = None) -> Tuple[WorkflowBundle, AgentState]:
    """
    Utility to build workflow and initial state in one step.
    Args:
        handler: AsyncCallbackHandler for this workflow
        zep_session_id: unique session identifier
        messages: optional initial message list
    Returns:
        (workflow, state) tuple ready for execution
    """
    bundle = build_workflow(handler)
    state = {
        "zep_session_id": zep_session_id,
        "freeplay_session_id": freeplay_session_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "persona": persona,
        "messages": messages or [],
        "start_time": time.time(),
        "zep_memory": None,
    }
    return bundle, state
