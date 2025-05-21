import asyncio
from pprint import pprint
from utils.freeplay_helpers import FreeplayClient
import datetime
import time

from tools import (
    PlayerSearchTool,
    GameSearchTool,
)


available_tools = [
    GameSearchTool(),
    PlayerSearchTool(),
]


template = "casual_fan_prompt"
environment = "latest"
variables = {
    "now": datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
    "zep_context": "Zep is your daddy",
}
# history = [
#     {"role": "user", "content": "what are some dinner ideas..."},
#     {"role": "assistant", "content": "all you should eat is steamed broccoli - you will live forever"},
#     {"role": "user", "content": "i don't want to live forever if all i eat is steamed broccoli"},
#     {"role": "assistant", "content": "silly human"},
# ]
# history = [
#     {'role': 'human', 'content': 'tell me about some players in everglade fc'},
#     # {'role': 'tool', 'content': '{"number": 23, "name": "Brian Davis", "age": 27, "nationality": "USA", "shirt_number"...c image full of energy and anticipation."}'},
#     # {'role': 'tool', 'content': '{"number": 10, "name": "Matthew Martin", "age": 24, "nationality": "USA", "shirt_numb...he dramatic flair he brings to the game."}'},
#     {'role': 'ai', 'content': 'Everglade FC is bursting with talent! Here are some standout players to watch:\n\n1. **...rglade FC brings to the field! Go, team! 🌟'},
# ]
history = [
    {'role': 'user', 'content': 'tell me about some players in everglade fc'},
    # {'role': 'assistant', 'content': ''},
    {'role': 'tool_call', 'content': '{"number": 23, "name": "Brian Davis", "age": 27, "nationality": "USA", "shirt_number"...c image full of energy and anticipation."}'},
    # {'role': 'tool', 'content': '{"number": 10, "name": "Matthew Martin", "age": 24, "nationality": "USA", "shirt_numb...he dramatic flair he brings to the game."}'},
    {'role': 'assistant', 'content': 'Everglade FC is bursting with talent! Here are some standout players to watch:\n\n1. **...rglade FC brings to the field! Go, team! 🌟'},
]

fp_client = FreeplayClient()
prompt = fp_client.get_prompt(template, environment)

formatted_prompt = prompt.bind(variables, history=history).format()


def main():
    print(formatted_prompt.llm_prompt)
    print('================')
    tool_schema = [tool.input_schema.schema_json() for tool in available_tools]
    print(tool_schema)
    print('================')

    state = {
        "start_time": time.time(),
        "messages": history,
    }
    # variables['history'] = history

    fp_client.create_session()
    fp_client.record_session(
        state=state,
        prompt_vars=variables,
        formatted_prompt=formatted_prompt,
    )

if __name__ == "__main__":
    main()
    