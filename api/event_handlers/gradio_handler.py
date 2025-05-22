import queue
from colorama import Fore, Style
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
from typing import List
from langchain_core.messages import BaseMessage

image_base = """
<img 
    src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/profiles/players_pics/{filename}"
    style="max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto;"
/>
"""
team_image_map = {
    'everglade-fc': 'Everglade_FC',
    'fraser-valley-united': 'Fraser_Valley_United',
    'tierra-alta-fc': 'Tierra_Alta_FC',
    'yucatan-force': 'Yucatan_Force',
}


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
        pass
        # self.info_box('[CHAT START]')
        # self.ots_box("""
        # <img 
        #     src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/landing.png"
        #     style="max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto;"
        # />
        # """)

    async def on_llm_new_token(self, token: str, **kwargs):
        if token:
            self.queue.put(token) 

    async def on_llm_end(self, result: LLMResult, *args, **kwargs):
        pass
        # if self.is_chat_stream_end(result):
        #     self.queue.put(None)

    async def on_tool_end(self, output: any, **kwargs):
        print(f"\n{Fore.CYAN}[TOOL END] {output}{Style.RESET_ALL}")
        for doc in output:
            if True:#doc.metadata.get("show_profile_card"):
                img = image_base.format(filename=self.get_image_filename(doc))
                print(f"\n{Fore.YELLOW}[TOOL END] {img}{Style.RESET_ALL}")
                self.ots_box(img)
                break
            # else:
                # self.info_box(doc)

    async def on_tool_start(self, input: any, *args, **kwargs):
        self.info_box(input.get("name", "[TOOL START]"))

    async def on_workflow_end(self, state, *args, **kwargs):
        print(f"\n{Fore.CYAN}[WORKFLOW END]{Style.RESET_ALL}")
        self.queue.put(None)
        # for msg in state["messages"]:
        #     print(f'{Fore.YELLOW}{msg.content}{Style.RESET_ALL}')

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
