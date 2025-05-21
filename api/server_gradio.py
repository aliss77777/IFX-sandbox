import asyncio
import gradio as gr
import time
import os
from pydantic import BaseModel
from threading import Thread
from langchain_core.messages import HumanMessage, AIMessage
from event_handlers.gradio_handler import GradioEventHandler
from workflows.base import build_workflow_with_state
from utils.freeplay_helpers import FreeplayClient
from utils.zep_helpers import ZepClient

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
show_state = True
dev_mode = os.getenv("DEV_MODE", "").lower() == "true"


class AppState(BaseModel):
    email: str = "huge@hugeinc.com"
    first_name: str = "Hugh"
    last_name: str = "Bigly"
    count: int = 0
    persona: str = "Casual Fan"
    history: list = []
    zep_session_id: str = ""
    freeplay_session_id: str = ""
    
    def ensure_sessions(self):
        if not self.zep_session_id:
            self.zep_session_id = ZepClient() \
                .get_or_create_user(self.email, self.first_name, self.last_name) \
                .create_session() \
                .session_id
        if not self.freeplay_session_id:
            self.freeplay_session_id = FreeplayClient().create_session().session_id

### Helpers ###

def submit_helper(state, handler, user_query):
    state.count += 1
    state.ensure_sessions()
    message = HumanMessage(content=user_query)
    state.history.append(message)
    state = AppState(**state.dict())
    yield state, ""

    # result = ""
    # for i in range(0, len(lorem_ipsum), 4):
    #     time.sleep(0.1)
    #     result += lorem_ipsum[i:i+4]
    #     yield state, result

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
        result += token
        yield state, result

    state.history.append(AIMessage(content=result))

### Interface ###

with gr.Blocks() as demo:
    state = gr.State(AppState())
    handler = GradioEventHandler()

    gr.Markdown("# Huge League Soccer")
    with gr.Row(scale=1):
        email = gr.Textbox(label="Email",
                           type="email",
                           interactive=True,
                           lines=1,
                           value=state.value.email)
        first_name = gr.Textbox(label="First Name",
                                lines=1,
                                interactive=True,
                                value=state.value.first_name)
        last_name = gr.Textbox(label="Last Name",
                               lines=1,
                               interactive=True,
                               value=state.value.last_name)
    llm_response = gr.Textbox(label="LLM Response", lines=10)

    with gr.Row(scale=1):
        with gr.Column(scale=1):
            persona = gr.Radio(
                choices=["Casual Fan", "Super Fan"],
                value="Casual Fan",
                label="Select Persona",
            )
        with gr.Column(scale=2):
            user_query = gr.Textbox(
                label="User Query",
                placeholder="Ask me about Huge League Soccer...",
                # lines=3,
                autofocus=True,
                show_label=False,
            )
            submit_btn = gr.Button("Submit", variant="primary", scale=0)

    clear_state_btn = gr.Button("Clear State", variant="stop", scale=1)

    with gr.Row(visible=show_state, variant="compact", scale=1):
        count_disp = gr.Number(
            label="Count",
            interactive=False,
            value=state.value.count,
            scale=0,
        )
        persona_disp = gr.Text(
            label="Persona",
            interactive=False,
            value=state.value.persona,
            scale=0
        )
        zep_session_id_disp = gr.Text(
            label="Zep Session ID",
            interactive=False,
            value=state.value.zep_session_id,
            scale=1
        )
        freeplay_session_id_disp = gr.Text(
            label="Freeplay Session ID",
            interactive=False,
            value=state.value.freeplay_session_id,
            scale=1
        )

    ### Events

    @state.change(inputs=[state], outputs=[count_disp, persona_disp, zep_session_id_disp, freeplay_session_id_disp])
    def state_change(state):
        return state.count, state.persona, state.zep_session_id, state.freeplay_session_id
    
    @clear_state_btn.click(outputs=[state, llm_response, persona, user_query, email, first_name, last_name])
    def clear_state():
        new_state = AppState()
        return new_state, "", new_state.persona, "", new_state.email, new_state.first_name, new_state.last_name

    # @submit_btn.click(inputs=[state, user_query], outputs=[state, llm_response])
    # def submit(state, user_query):
    #     state.count += 1
    #     state.ensure_sessions()
    #     state = AppState(**state.dict())

    #     user_query = user_query or "tell me about some players in everglade fc"
    #     message = HumanMessage(content=user_query)
    #     state.history.append(message)

    #     result = ""
    #     yield state, result
    #     for i in range(0, len(lorem_ipsum), 4):
    #         time.sleep(0.1)
    #         result += lorem_ipsum[i:i+4]
    #         yield state, result


    @submit_btn.click(inputs=[state, user_query], outputs=[state, llm_response])
    def submit(state, user_query):
        user_query = user_query or "tell me about some players in everglade fc"
        yield from submit_helper(state, handler, user_query)
        
    
    # @submit_btn.click(inputs=[user_query, state], outputs=[llm_response, zep_session_id_disp, freeplay_session_id_disp])
    # def submit(user_query, state):
    #     state.ensure_sessions()
    #     state.user_query = user_query or "tell me about some players in everglade fc"
    #     message = HumanMessage(content=state.user_query)
    #     state.history.append(message)
    #     # workflow_state["messages"] = state.history

    #     def start_async_loop():
    #         workflow, workflow_state = build_workflow_with_state(
    #             handler=handler,
    #             zep_session_id=state.zep_session_id,
    #             freeplay_session_id=state.freeplay_session_id,
    #             email=state.email,
    #             first_name=state.first_name,
    #             last_name=state.last_name,
    #             persona=state.persona,
    #             messages=state.history,
    #         )

    #         async def run_workflow():
    #             await workflow.ainvoke(workflow_state)
            
    #         asyncio.run(run_workflow())

    #     thread = Thread(target=start_async_loop, daemon=True)
    #     thread.start()

    #     result = ""
    #     while True:
    #         token = handler.queue.get()
    #         # from colorama import Fore, Style
    #         # print(f'{Fore.GREEN}{token}{Style.RESET_ALL}')
    #         if token is None:
    #             break
    #         if isinstance(token, dict):
    #             if token["type"] == "info":
    #                 gr.Info(token["message"])
    #                 continue
    #         result += token
    #         yield result, state.zep_session_id, state.freeplay_session_id

    #     state.history.append(AIMessage(content=result))

    # @user_query.submit(inputs=[user_query, state], outputs=[llm_response, state])
    # def user_query_change(user_query, state):
    #     state.user_query = user_query
    #     state.zep_session_id = f"zep_{int(time.time())}"
    #     state.freeplay_session_id = f"freeplay_{int(time.time())}"

    #     result = state.user_query 
    #     for i in range(0, len(lorem_ipsum), 4):
    #         time.sleep(0.1)
    #         result += lorem_ipsum[i:i+4]
    #         yield result, state

    @persona.change(inputs=[persona, state], outputs=[persona_disp])
    def persona_change(persona, state):
        state.persona = persona
        return persona

    # @submit_btn.click(inputs=[state], outputs=[state, llm_response])
    # def submit(state):
    #     state.count += 1
    #     new_state = AppState(**state.dict()) 
    #     result = 'hello'
    #     for i in range(0, len(lorem_ipsum), 4):
    #         time.sleep(0.1)
    #         result += lorem_ipsum[i:i+4]
    #         yield new_state, result

    # @user_query.submit(inputs=[state], outputs=[count_disp, user_query])
    # def user_query_change(state):
    #     state.count += 1
    #     return state.count, ''

    # @clear_state_btn.click(inputs=[state], outputs=[count_disp, persona_disp, user_query, llm_response, zep_session_id_disp, freeplay_session_id_disp])
    # def clear_state(state):
    #     state.clear()
    #     return state.count, state.persona, state.user_query, "", state.zep_session_id, state.freeplay_session_id

    # @email.change(inputs=[email, state])
    # def email_change(email, state):
    #     state.email = email

    # @first_name.change(inputs=[first_name, state])
    # def first_name_change(first_name, state):
    #     state.first_name = first_name

    # @last_name.change(inputs=[last_name, state])
    # def last_name_change(last_name, state):
    #     state.last_name = last_name

    # @state.change(inputs=[state], outputs=[gr.ParamViewer()])
    # def state_change(state):
    #     # return state.zep_session_id, state.freeplay_session_id
    #     docs = {
    #         "zep_session_id_ZZZZ": {
    #             "default": "None\n",
    #             "type": "str | None\n",
    #             "description": "Zep session ID.",
    #         },
    #     }

    #     return gr.ParamViewer(docs)


if __name__ == "__main__":
    if dev_mode:
        demo.launch(server_name="0.0.0.0", server_port=8000)
    else:
        demo.launch(server_name="0.0.0.0")
