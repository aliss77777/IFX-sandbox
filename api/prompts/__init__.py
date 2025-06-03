from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import (
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessage,
)

from .system_prompts import casual_fan_prompt, super_fan_prompt

casual_fan_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(casual_fan_prompt),
    MessagesPlaceholder("input")
])

super_fan_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(super_fan_prompt),
    MessagesPlaceholder("input")
])
