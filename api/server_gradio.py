import asyncio
import gradio as gr
import time
from pydantic import BaseModel
from threading import Thread
from langchain_core.messages import HumanMessage, AIMessage
from event_handlers.gradio_handler import GradioEventHandler
from workflows.base import build_workflow

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
show_state = True


class AppState(BaseModel):
    count: int = 0
    persona: str = "Casual Fan"
    user_query: str = ""
    history: list = []
    
    def clear(self) -> None:
        """Reset the state to default values."""
        self.count = 0
        self.persona = "Casual Fan"
        self.user_query = ""
        self.history = []


with gr.Blocks() as demo:
    state = gr.State(AppState())
    handler = GradioEventHandler()
    workflow_state = {
        "session_id": "5aed14ff09fb415ba77439409f458909",
        "messages": [],
    }

    gr.Markdown("# Huge League Soccer")
    llm_response = gr.Textbox(label="LLM Response", lines=10)
    count = gr.Number(
        label="Count",
        interactive=False,
        visible=show_state,
    )
    persona_disp = gr.Text(
        label="Persona",
        interactive=False,
        value=state.value.persona,
        visible=show_state,
    )

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
    
    @submit_btn.click(inputs=[user_query, state], outputs=[llm_response])
    def submit(user_query, state):
        state.user_query = user_query or "tell me about some players in everglade fc"
        message = HumanMessage(content=state.user_query)
        state.history.append(message)
        workflow_state["messages"] = state.history

        def start_async_loop():
            workflow = build_workflow(handler)
            async def run_workflow():
                print(workflow_state)
                await workflow.ainvoke(workflow_state)
            asyncio.run(run_workflow())

        thread = Thread(target=start_async_loop, daemon=True)
        thread.start()

        result = ""
        while True:
            token = handler.queue.get()
            from colorama import Fore, Style
            print(f'{Fore.GREEN}{token}{Style.RESET_ALL}')
            if token is None:
                break
            if isinstance(token, dict):
                if token["type"] == "info":
                    gr.Info(token["message"])
                    continue
            result += token
            yield result

        state.history.append(AIMessage(content=result))

    @user_query.submit(inputs=[user_query, state], outputs=[llm_response])
    def user_query_change(user_query, state):
        state.user_query = user_query

        result = state.user_query 
        for i in range(0, len(lorem_ipsum), 4):
            time.sleep(0.1)
            result += lorem_ipsum[i:i+4]
            yield result

    @persona.change(inputs=[persona, state], outputs=[persona_disp])
    def persona_change(persona, state):
        state.persona = persona
        return persona

    @submit_btn.click(inputs=[state], outputs=[count])
    def submit(state):
        state.count += 1
        return state.count

    @user_query.submit(inputs=[state], outputs=[count, user_query])
    def user_query_change(state):
        state.count += 1
        return state.count, ''

    @clear_state_btn.click(inputs=[state], outputs=[count, persona_disp, user_query, llm_response])
    def clear_state(state):
        state.clear()
        return state.count, state.persona, state.user_query, ""


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8000)
