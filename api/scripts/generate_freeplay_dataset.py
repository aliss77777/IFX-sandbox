import json
import os
import datetime


def export_dict_as_jsonl(data: dict, filename: str):
    """
    Export a dictionary as a JSONL file.
    """
    with open(filename, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


"""
        {
            "inputs": {"": ""},
            "output": "",
        },
"""


if __name__ == "__main__":
    data = [
        {
            "inputs": {
                "now": datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d'),
                "zep_context": "Zep is your daddy",
                "history": [
                    {"role": "user", "content": "what are some dinner ideas..."},
                    # {"role": "assistant", "content": "here are some dinner ideas..."},
                ],
            },
            "output": "here are some dinner ideas...",
        },
    ]
    # export dict as jsonl
    export_dict_as_jsonl(data, "formatted_prompt.jsonl")
