import os
import uuid
import datetime
from zep_cloud.client import Zep
from zep_cloud.types import Message
from langchain.chat_models import init_chat_model
import colorama
from colorama import Fore, Style
from pprint import pprint, pformat

from prompts import (
    casual_fan_prompt,
    HumanMessage,
    AIMessage,
)
from tools import (
    PlayerSearchTool,
    GameSearchTool,
)

API_KEY = os.environ.get('ZEP_API_KEY')

client = Zep(
    api_key=API_KEY,
)
model = init_chat_model("gpt-4o-mini", model_provider="openai")
available_tools = [
    PlayerSearchTool(),
    GameSearchTool(),
]


def create_user(email, first_name, last_name):
    # Create a new user
    new_user = client.user.add(
        user_id=email,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    return new_user


def create_session(user_id):
# Generate a unique session ID
    session_id = uuid.uuid4().hex
    # Create a new session for the user
    client.memory.add_session(
        session_id=session_id,
        user_id=user_id,
    )
    return session_id


def add_fact(user_id, fact):
    new_episode = client.graph.add(
        user_id=user_id,
        type="text",
        data=fact,
    )
    return new_episode


history = []
def send_message(session_id, message):
    global history
    history.append(HumanMessage(content=message))
    # always cap history at last 6 messages
    history = history[-6:]

    memory = client.memory.get(session_id=session_id)
    print(Fore.LIGHTBLACK_EX + "\nMemory retrieved." + Style.RESET_ALL)
    # print(Fore.YELLOW + pformat(memory.context, compact=False, width=120) + "\n" + Style.RESET_ALL)

    prompt = casual_fan_prompt.format(
        zep_context=memory.context,
        input=history,
        now=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
    )

    print(Fore.YELLOW + pformat(prompt, compact=False, width=120) + "\n" + Style.RESET_ALL)

    chunks = []
    for chunk in model.stream(prompt, tools=available_tools):
        chunks.append(chunk)
        print(Fore.GREEN + chunk.content + Style.RESET_ALL, end="", flush=True)

    messages = [
        Message(
            role="user",
            content=message,
            role_type="user",
        ),
        Message(
            role="assistant",
            content="".join([chunk.content for chunk in chunks]),
            role_type="assistant",
        ),
    ]
    client.memory.add(session_id=session_id, messages=messages)
    print(Fore.LIGHTBLACK_EX + "\nMemory updated." + Style.RESET_ALL)

    history.append(
        AIMessage(content="".join([chunk.content for chunk in chunks]))
    )
    
    return chunks


user_id = 'rbalch@hugeinc.com'
# session_id = 'f0bfaa5b4b11486391e1c52bcebe0ad3' # blue sky
# session_id = '9f0a03443fa44eb9a1e9967ad2ab137a'
session_id = '5aed14ff09fb415ba77439409f458909'

# user = client.user.get(user_id)
# memory = client.memory.get(session_id=session_id)
# print(memory)


# if __name__ == "__main__":
#     """
#     Simple REPL loop for sending messages to the LLM.
#     Prompts with '>', sends input to send_message, and prints response in green.
#     Type 'exit' or press Ctrl+C to quit.
#     """
#     colorama.init(autoreset=True)

#     print("\nType 'exit' or press Ctrl+C to quit.\n")
#     try:
#         while True:
#             user_input = input("> ")
#             if user_input.strip().lower() == "exit":
#                 print("Exiting.")
#                 break
#             # Call send_message and print LLM response in green
#             chunks = send_message(session_id, user_input)
#             print("")  # Newline after response
#     except KeyboardInterrupt:
#         print("\nExiting.")


# from prompts import (
#     casual_fan_prompt,
#     HumanMessage,
#     AIMessage,
# )



memory = client.memory.get(session_id=session_id)

history = [
    HumanMessage(content="tell me about some players in everglade fc"),
    # AIMessage(content="soccer is the best sport ever"),
]

prompt = casual_fan_prompt.format(
    zep_context=memory.context,
    input=history,
    now=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
)

print(prompt)
