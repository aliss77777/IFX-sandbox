# import datetime
import os
import time
from functools import lru_cache
from typing import Union, Optional, List, Any, Dict
from freeplay import Freeplay, RecordPayload, ResponseInfo, CallInfo
from freeplay.resources.prompts import FormattedPrompt
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool


def safe_get_content(obj: Any) -> Any:
    """
    Safely get the 'content' from an object whether it's a dictionary or an object with attributes.
    
    Args:
        obj: An object that might have 'content' as either a dictionary key or an attribute
        
    Returns:
        The content value if available
        
    Raises:
        AttributeError: If content cannot be accessed either as a dict key or object attribute
    """
    # Try dictionary access first
    if isinstance(obj, dict) and "content" in obj:
        return obj["content"]
    
    # Try attribute access next
    if hasattr(obj, "content"):
        return obj.content
    
    # If neither works, raise an exception
    raise AttributeError(f"Cannot access 'content' on {type(obj).__name__} object. It's neither a dict with 'content' key nor an object with 'content' attribute.")

FREEPLAY_PROJECT_ID = os.getenv("FREEPLAY_PROJECT_ID")
_role_map = {
    'human': 'user',
    'ai': 'assistant',
    'tool': 'tool',
}

# @lru_cache(maxsize=1)
def _get_fp_client():
    return Freeplay(
        freeplay_api_key=os.getenv("FREEPLAY_API_KEY"),
        api_base=os.getenv("FREEPLAY_URL"),
    )


class FreeplayClient:

    def __init__(
        self,
        fp_client: Freeplay = None,
        tools: List[BaseTool] = None,
    ):
        self.fp_client = fp_client or _get_fp_client()
        self.session = None
        self.session_id = None
        self.trace = None
        self.tools = tools
        self.tool_schema = self._convert_tool_schema(self.tools) if tools else None
        # cache variables for recording
        self._prompt_cache = {}
        self._prompt_vars = None
        self._formatted_prompt = None
    
    def create_session(self):
        # create a Freeplay session
        self.session = self.fp_client.sessions.create()
        self.session_id = self.session.session_id
        return self

    def create_trace(self, input: str, agent_name: str, custom_metadata: dict = {}):
        # make sure we have a session
        if not self.session:
            self.create_session()
        # create the trace
        self.trace = self.session.create_trace(
            input=input,
            agent_name=agent_name,
            custom_metadata=custom_metadata,
        )
        return self

    @staticmethod
    def get_fp_client():
        return _get_fp_client()

    # retreive and format your prompt
    def get_formatted_prompt(
        self,
        template: str,
        environment: str = "latest",
        variables: dict = {},
        history: Optional[List[BaseMessage]] = None,
    ):
        """
        Get a formatted prompt from Freeplay.
        """
        formatted_prompt = self.fp_client.prompts.get_formatted(
            project_id=FREEPLAY_PROJECT_ID,
            template_name=template,
            environment=environment,
            variables=variables,
            history=history,
        )
        return formatted_prompt

    def get_prompt(
        self,
        template: str,
        environment: str = "latest",
    ):
        """
        Get an unformatted prompt template from Freeplay.
        """
        key = self._make_cache_key(template, environment)
        if key in self._prompt_cache:
            return self._prompt_cache[key]
        template_prompt = self.fp_client.prompts.get(
            project_id=FREEPLAY_PROJECT_ID,
            template_name=template,
            environment=environment
        )
        self._prompt_cache[key] = template_prompt
        return template_prompt

    def _make_cache_key(self, template: str, environment: str) -> tuple:
        """
        Create a cache key for the prompt cache.
        The key is a tuple of (template, environment).
        Args:
            template (str): The prompt template name.
            environment (str): The environment name.
        Returns:
            tuple: (template, environment)
        """
        return (template, environment)

    def record_session(
        self,
        state,
        end: Optional[float] = time.time(),
        formatted_prompt: Optional[FormattedPrompt] = None,
        prompt_vars: Optional[dict] = None,
    ):
        prompt_vars = prompt_vars or self._prompt_vars
        formatted_prompt = formatted_prompt or self._formatted_prompt

        # all_messages = formatted_prompt.all_messages(
        #     new_message={'role': 'assistant', 'content': safe_get_content(state['messages'][-1])}
        # )

        # convert messages to Freeplay format
        if state['messages'] and isinstance(state['messages'][0], dict):
            # if it's a dict leave it alone and just send it on
            all_messages = state['messages']
        else:
            all_messages = self._convert_messages(state['messages'])

        # fix session if we landed here and it's missing
        if not self.session:
            self.session = self.fp_client.sessions.restore_session(session_id=state['freeplay_session_id'])
            self.session_id = self.session.session_id

        # record your LLM call with Freeplay
        payload = RecordPayload(
            all_messages=all_messages,
            inputs=prompt_vars,
            session_info=self.session.session_info, 
            prompt_info=formatted_prompt.prompt_info,
            call_info=CallInfo.from_prompt_info(formatted_prompt.prompt_info, start_time=state['start_time'], end_time=end), 
            response_info=ResponseInfo(
                # is_complete=chat_response.choices[0].finish_reason == 'stop'
                is_complete=True
            ),
            trace_info=self.trace,
            tool_schema=self.tool_schema,
        )
        self.fp_client.recordings.create(payload)

    def record_trace(
        self,
        state,
        agent_name: Optional[str] = None,
        custom_metadata: dict = {},
        end: Optional[float] = time.time(),
        formatted_prompt: Optional[FormattedPrompt] = None,
        prompt_vars: Optional[dict] = None,
    ):
        """
        Create and record a trace with Freeplay.
        """
        input = safe_get_content(state['messages'][0])
        self.create_trace(
            input=input,
            agent_name=agent_name,
            custom_metadata=custom_metadata,
        )
        self.record_session(
            state=state,
            end=end,
            formatted_prompt=formatted_prompt,
            prompt_vars=prompt_vars,
        )
        self.trace.record_output(
            FREEPLAY_PROJECT_ID,
            safe_get_content(state['messages'][-1])
        )

    def get_prompt_by_persona(self,
                              persona: str,
                              variables: dict = {},
                              history: Optional[List[BaseMessage]] = None):
        if 'casual' in persona.lower():
            prompt = self.get_prompt(template='casual_fan_prompt', environment='latest')
        elif 'super' in persona.lower():
            prompt = self.get_prompt(template='super_fan_prompt', environment='latest')
        else:
            raise ValueError(f"Unknown persona: {persona}")

        formatted_prompt = prompt.bind(variables=variables, history=history).format()
        self._prompt_vars = variables
        self._formatted_prompt = formatted_prompt

        return formatted_prompt

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert LangChain messages to dictionary format. Note this maps to OpenAI's message format."""
        converted = []
        role_map = {
            HumanMessage: "user",
            AIMessage: "assistant",
            SystemMessage: "system",
            ToolMessage: "tool",
        }

        for msg in messages:
            # Get role, default to "user" if unknown type
            role = role_map.get(type(msg), "user")

            # Create message dict with special handling for tool messages
            if role == "tool":
                msg_dict = {
                    "role": role,
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id,
                    "name": msg.name,
                }
            else:
                msg_dict = {
                    "role": role,
                    "content": msg.content,
                }

            # Add tool calls if present
            if (
                hasattr(msg, "additional_kwargs")
                and msg.additional_kwargs
                and "tool_calls" in msg.additional_kwargs
            ):
                msg_dict["tool_calls"] = msg.additional_kwargs["tool_calls"]

            converted.append(msg_dict)

        return converted

    def _convert_tool_schema(self, tools: List[BaseTool]) -> List[Dict[str, Any]]:
        """Convert LangChain tools to Freeplay tool schema format."""
        tool_schema = []
        for tool in tools:
            # Extract parameters from tool's args_schema
            parameters = {"type": "object", "properties": {}, "required": []}
            if hasattr(tool, "args_schema") and tool.args_schema:
                schema = tool.args_schema.model_json_schema()
                parameters.update(
                    {
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    }
                )

            tool_schema.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or tool.name,
                        "parameters": parameters,
                    },
                }
            )
        return tool_schema
