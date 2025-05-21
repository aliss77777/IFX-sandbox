# import datetime
import os
import time
from functools import lru_cache
from typing import Union, Optional, List
from freeplay import Freeplay, RecordPayload, ResponseInfo, CallInfo
from freeplay.resources.prompts import FormattedPrompt
from langchain_core.messages import BaseMessage

FREEPLAY_PROJECT_ID = os.getenv("FREEPLAY_PROJECT_ID")


# @lru_cache(maxsize=1)
def _get_fp_client():
    return Freeplay(
        freeplay_api_key=os.getenv("FREEPLAY_API_KEY"),
        api_base=os.getenv("FREEPLAY_URL"),
    )


class FreeplayClient:

    def __init__(self, fp_client: Freeplay = None):
        self.fp_client = fp_client or _get_fp_client()
        self.session = None
        self.session_id = None
        # cache variables for recording
        self._prompt_cache = {}
        self._prompt_vars = None
        self._formatted_prompt = None

    def create_session(self):
        # create a Freeplay session
        self.session = self.fp_client.sessions.create()
        self.session_id = self.session.session_id
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

        # convert messages to Freeplay format
        if state['messages'] and isinstance(state['messages'][0], dict):
            all_messages = state['messages']
        else:
            all_messages = [{'role': m.type, 'content': m.content} for m in state['messages'] if m.content]

        # fix session if we landed here and it's missing
        if not self.session:
            self.session = self.fp_client.sessions.restore_session(session_id=state['freeplay_session_id'])
            self.session_id = self.session.session_id

        # record your LLM call with Freeplay
        payload = RecordPayload(
            all_messages=all_messages,
            inputs=prompt_vars,
            session_info=self.session, 
            prompt_info=formatted_prompt.prompt_info,
            call_info=CallInfo.from_prompt_info(formatted_prompt.prompt_info, start_time=state['start_time'], end_time=end), 
            response_info=ResponseInfo(
                # is_complete=chat_response.choices[0].finish_reason == 'stop'
                is_complete=True
            )
        )
        self.fp_client.recordings.create(payload)

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
