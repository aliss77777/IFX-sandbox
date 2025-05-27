import asyncio
import gradio as gr
import os
from pydantic import BaseModel, field_validator
from threading import Thread
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from event_handlers.gradio_handler import GradioEventHandler
from workflows.base import build_workflow_with_state
from utils.freeplay_helpers import FreeplayClient
from utils.zep_helpers import ZepClient

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
show_state = True
fake_response = False
dev_mode = os.getenv("DEV_MODE", "").lower() == "true"
MESSAGE_TYPE_MAP = {
    "human": HumanMessage,
    "ai": AIMessage,
    # Add other message types as needed
}
ots_default = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; max-width: 727px; height: 363px; margin: 0 auto;">
    {content}
</div>
"""


class AppState(BaseModel):
    email: str = "huge@hugeinc.com"
    first_name: str = "Hugh"
    last_name: str = "Bigly"
    count: int = 0
    persona: str = "Casual Fan"
    history: list = []
    zep_session_id: str = ""
    freeplay_session_id: str = ""
    ots_content: str = ots_default.format(content="""
    <img 
        src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/huge_landing.png"
        style="max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto;"
    />
    """)
    
    def ensure_sessions(self):
        if not self.zep_session_id:
            self.zep_session_id = ZepClient() \
                .get_or_create_user(self.email, self.first_name, self.last_name) \
                .create_session() \
                .session_id
        if not self.freeplay_session_id:
            self.freeplay_session_id = FreeplayClient().create_session().session_id

    @field_validator("history", mode="before")
    @classmethod
    def validate_history(cls, v):
        out = []
        for item in v:
            if isinstance(item, BaseMessage):
                out.append(item)
            elif isinstance(item, dict):
                out.append(MESSAGE_TYPE_MAP[item["type"]](**item))
            else:
                raise TypeError(f"Invalid type in history: {type(item)}")
        return out
            

### Helpers ###

def submit_helper(state, handler, user_query):
    state.count += 1
    state.ensure_sessions()
    message = HumanMessage(content=user_query)
    state.history.append(message)
    state = AppState(**state.model_dump())
    yield state, ""

    if fake_response:
        result = lorem_ipsum
        for i in range(0, len(lorem_ipsum), 4):
            time.sleep(0.1)
            result += lorem_ipsum[i:i+4]
            yield state, result
        return

    def start_async_loop():
        workflow_bundle, workflow_state = build_workflow_with_state(
            handler=handler,
            zep_session_id=state.zep_session_id,
            freeplay_session_id=state.freeplay_session_id,
            email=state.email,
            first_name=state.first_name,
            last_name=state.last_name,
            persona=state.persona,
            messages=state.history,
        )

        async def run_workflow():
            await workflow_bundle.workflow.ainvoke(workflow_state)
        
        asyncio.run(run_workflow())

    thread = Thread(target=start_async_loop, daemon=True)
    thread.start()

    result = ""
    while True:
        token = handler.queue.get()
        # from colorama import Fore, Style
        # print(f'{Fore.GREEN}{token}{Style.RESET_ALL}')
        if token is None:
            break
        if isinstance(token, dict):
            if token["type"] == "info":
                gr.Info(token["message"])
                continue
            if token["type"] == "ots":
                print('OTS: ' + token["message"])
                state.ots_content = ots_default.format(content=token["message"])
                state = AppState(**state.model_dump())
                continue
        result += token
        yield state, result
    
    state.history.append(AIMessage(content=result))

### Interface ###

with gr.Blocks(theme="soft") as demo:
    state = gr.State(AppState())
    handler = GradioEventHandler()

    gr.Markdown("# Huge League Soccer")
    with gr.Row():
        email = gr.Textbox(label="Email",
                           type="email",
                           interactive=True,
                           lines=1,
                           value=state.value.email,
                           scale=1)
        first_name = gr.Textbox(label="First Name",
                                lines=1,
                                interactive=True,
                                value=state.value.first_name,
                                scale=1)
        last_name = gr.Textbox(label="Last Name",
                               lines=1,
                               interactive=True,
                               value=state.value.last_name,
                               scale=1)

    with gr.Row():
        with gr.Column(scale=3):
            llm_response = gr.Textbox(label="LLM Response", lines=15)
        with gr.Column(scale=2):
            ots_box = gr.HTML(
                label="OTS",
                value=state.value.ots_content,
            )

    with gr.Row():
        with gr.Column(scale=1, min_width=200):
            persona = gr.Radio(
                choices=["Casual Fan", "Super Fan"],
                value="Casual Fan",
                label="Select Persona",
            )
        with gr.Column(scale=3):
            user_query = gr.Textbox(
                label="User Query",
                placeholder="Ask me about Huge League Soccer...",
                autofocus=True,
                show_label=False,
            )
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary", scale=1)
                clear_state_btn = gr.Button("Clear State", scale=1)

    with gr.Row(visible=show_state, variant="compact"):
        count_disp = gr.Number(
            label="Count",
            interactive=False,
            value=state.value.count,
            scale=1,
        )
        persona_disp = gr.Text(
            label="Persona",
            interactive=False,
            value=state.value.persona,
            scale=1
        )
        zep_session_id_disp = gr.Text(
            label="Zep Session ID",
            interactive=False,
            value=state.value.zep_session_id,
            scale=2
        )
        freeplay_session_id_disp = gr.Text(
            label="Freeplay Session ID",
            interactive=False,
            value=state.value.freeplay_session_id,
            scale=2
        )

    ### Events

    @state.change(inputs=[state], outputs=[count_disp, persona_disp, zep_session_id_disp, freeplay_session_id_disp, user_query, ots_box])
    def state_change(state):
        return state.count, state.persona, state.zep_session_id, state.freeplay_session_id, "", state.ots_content
    
    @clear_state_btn.click(outputs=[state, llm_response, persona, user_query, email, first_name, last_name])
    def clear_state():
        new_state = AppState()
        return new_state, "", new_state.persona, "", new_state.email, new_state.first_name, new_state.last_name

    @submit_btn.click(inputs=[state, user_query], outputs=[state, llm_response])
    def submit(state, user_query):
        # user_query = user_query or "tell me about some players in everglade fc"
        user_query = user_query or "tell me about Ryan Martinez of everglade fc"
        yield from submit_helper(state, handler, user_query)
        
    @user_query.submit(inputs=[state, user_query], outputs=[state, llm_response])
    def user_query_change(state, user_query):
        # user_query = user_query or "tell me about some players in everglade fc"
        user_query = user_query or "tell me about Ryan Martinez of everglade fc"
        yield from submit_helper(state, handler, user_query)

    @persona.change(inputs=[persona, state], outputs=[persona_disp])
    def persona_change(persona, state):
        state.persona = persona
        return persona


if __name__ == "__main__":
    if dev_mode:
        demo.launch(server_name="0.0.0.0", server_port=8000)
    else:
        demo.launch(server_name="0.0.0.0")
