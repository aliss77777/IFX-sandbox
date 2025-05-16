# import datetime
import os
from functools import lru_cache
from typing import Union, Optional, List
from freeplay import Freeplay, RecordPayload, ResponseInfo, CallInfo
from langchain_core.messages import BaseMessage

FREEPLAY_PROJECT_ID = os.getenv("FREEPLAY_PROJECT_ID")


# @lru_cache(maxsize=1)
def get_fp_client():
    return Freeplay(
        freeplay_api_key=os.getenv("FREEPLAY_API_KEY"),
        api_base=os.getenv("FREEPLAY_URL"),
    )


# retreive and format your prompt
def get_formatted_prompt(
    template: str,
    environment: str = "latest",
    variables: dict = {},
    history: Optional[List[BaseMessage]] = None,
):
    """
    Get a formatted prompt from Freeplay.
    """
    # get fp client
    fpClient = get_fp_client()
    # variables = {**variables, "now": datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')}
    # get formatted prompt
    formatted_prompt = fpClient.prompts.get_formatted(
        project_id=FREEPLAY_PROJECT_ID,
        template_name=template,
        environment=environment,
        variables=variables,
        history=history
    )
    return formatted_prompt


async def get_prompt(
    template: str,
    environment: str = "latest",
):
    """
    Get an unformatted prompt template from Freeplay.
    """
    # get fp client
    fpClient = get_fp_client()
    # get unformatted prompt template
    template_prompt = fpClient.prompts.get(
        project_id=FREEPLAY_PROJECT_ID,
        template_name=template,
        environment=environment
    )
    return template_prompt
