import queue
from colorama import Fore, Style
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
from typing import List
from langchain_core.messages import BaseMessage


class GradioEventHandler(AsyncCallbackHandler):
    """
    Example async event handler: prints streaming tokens and tool results.
    Replace with websocket or other side effects as needed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue.Queue()

    def info_box(self, message: str):
        self.queue.put(
            {
                "type": "info",
                "message": message,
            }
        )

    def ots_box(self, message: str):
        self.queue.put(
            {
                "type": "ots",
                "message": message,
            }
        )

    async def on_chat_model_start(self, *args, **kwargs):
        self.info_box('[CHAT START]')
        self.ots_box("""
        <img 
            src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/landing.png"
            style="max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto;"
        />
        """)

    async def on_llm_new_token(self, token: str, **kwargs):
        if token:
            self.queue.put(token) 

    async def on_llm_end(self, result: LLMResult, *args, **kwargs):
        if self.is_chat_stream_end(result):
            self.queue.put(None)

    async def on_tool_end(self, output: any, **kwargs):
        print(f"\n{Fore.CYAN}[TOOL RESULT] {output}{Style.RESET_ALL}")

    async def on_tool_start(self, input: any, *args, **kwargs):
        self.info_box(f"[TOOL START]")

    async def on_workflow_end(self, state, *args, **kwargs):
        print(f"\n{Fore.CYAN}[WORKFLOW END]{Style.RESET_ALL}")
        for msg in state["messages"]:
            print(f'{Fore.YELLOW}{msg.content}{Style.RESET_ALL}')

    @staticmethod
    def is_chat_stream_end(result: LLMResult) -> bool:
        try:
            content = result.generations[0][0].message.content
            return bool(content and content.strip())
        except (IndexError, AttributeError):
            return False
