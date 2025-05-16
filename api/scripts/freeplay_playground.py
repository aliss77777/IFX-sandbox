import asyncio
from pprint import pprint
from utils.freeplay_helpers import get_formatted_prompt, get_prompt
import datetime

async def main():
    template = "casual_fan_prompt"
    environment = "latest"
    variables = {
        "now": datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
        "zep_context": "Zep is your daddy",
    }
    history = [
        {"role": "user", "content": "what are some dinner ideas..."},
        {"role": "assistant", "content": "here are some dinner ideas..."},
    ]

    prompt = get_formatted_prompt(template, environment, variables, history=history)
    # print(prompt.system_content)
    pprint(prompt.llm_prompt)

    # template_prompt = await get_prompt(template, environment)
    # print(template_prompt.messages)

if __name__ == "__main__":
    asyncio.run(main())
    