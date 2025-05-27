from colorama import Fore, Style
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
from typing import List
from langchain_core.messages import BaseMessage

image_base = """
<img 
    src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/profiles/{filename}"
    style="max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto;"
/>
"""
team_image_map = {
    'everglade-fc': 'Everglade_FC',
    'fraser-valley-united': 'Fraser_Valley_United',
    'tierra-alta-fc': 'Tierra_Alta_FC',
    'yucatan-force': 'Yucatan_Force',
}

class PrintEventHandler(AsyncCallbackHandler):
    """
    Example async event handler: prints streaming tokens and tool results.
    Replace with websocket or other side effects as needed.
    """

    def __init__(self, *args, **kwargs):
        print('[INIT]')
        super().__init__(*args, **kwargs)

    async def on_chat_model_start(self, *args, **kwargs):
        print('[CHAT START]')

    async def on_llm_new_token(self, token: str, **kwargs):
        if token:
            print(Fore.YELLOW + token + Style.RESET_ALL, end="", flush=True)

    async def on_llm_end(self, result: LLMResult, *args, **kwargs):
        if self.is_chat_stream_end(result):
            print('\n[END]')

    async def on_tool_end(self, output: any, **kwargs):
        for doc in output:
            if doc.metadata.get("show_profile_card"):
                img = image_base.format(filename=self.get_image_filename(doc))
                print(f"\n{Fore.CYAN}[TOOL RESULT] {img}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}[TOOL RESULT] {doc}{Style.RESET_ALL}")

    async def on_tool_start(self, input: any, *args, **kwargs):
        print(f"\n{Fore.CYAN}[TOOL START]{Style.RESET_ALL}")

    async def on_workflow_end(self, state, *args, **kwargs):
        print(f"\n{Fore.CYAN}[WORKFLOW END]{Style.RESET_ALL}")

    @staticmethod
    def is_chat_stream_end(result: LLMResult) -> bool:
        try:
            content = result.generations[0][0].message.content
            return bool(content and content.strip())
        except (IndexError, AttributeError):
            return False

    @staticmethod
    def get_image_filename(doc):
        return f'{team_image_map.get(doc.metadata.get("team"))}_{doc.metadata.get("number")}.png'

    # def __getattribute__(self, name):
    #     attr = super().__getattribute__(name)
    #     if callable(attr) and name.startswith("on_"):
    #         async def wrapper(*args, **kwargs):
    #             print(f"[EVENT] {name} args={args} kwargs={kwargs}")
    #             return await attr(*args, **kwargs)
    #         return wrapper
    #     return attr
