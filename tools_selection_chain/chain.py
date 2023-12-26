from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessage,
    SystemMessagePromptTemplate,
    SystemMessage
)
from typing import Sequence, Union
from .prompt import SYSTEM_MESSAGE, HUMAN_MESSAGE, FORMAT_INSTRUCTION

class ToolsSelectionInput(BaseModel):
  name: str
  objective: str
  constraints: str
  plans: str

def _extract_tool_properties(tool: Union[BaseTool, StructuredTool]) -> str:
  if tool.args_schema is None:
    return ""

  schema = tool.args_schema.schema()
  return " | ".join(
      [
          f"{name}: {prop['type']}, {prop['description']}."
          for name, prop in schema['properties'].items()
      ]
  )

def create_tools_selection_chain(
  llm: BaseLanguageModel,
  tools: Sequence[Union[BaseTool, StructuredTool]] = None,
):
  formated_tools = [
    f"{idx+1}. {tool.name}: {tool.description}.. Params: ({_extract_tool_properties(tool)})"
    for idx, tool in enumerate(tools)
  ]

  messages = [
    SystemMessagePromptTemplate.from_template(
      SYSTEM_MESSAGE,
      partial_variables={"tools": "\n".join(formated_tools)}
    ),
    HumanMessage(content=HUMAN_MESSAGE),
    SystemMessage(content=FORMAT_INSTRUCTION)
  ]
  prompt = ChatPromptTemplate.from_messages(messages)

  chain = (
    {
      "name": lambda x: x['name'],
      "name": lambda x: x['name'],
      "objective": lambda x: x['objective'],
      "constraints": lambda x: x['constraints'],
      "plans": lambda x: x['plans'],
    }
    |
    prompt
    |
    llm
  )
  return chain

