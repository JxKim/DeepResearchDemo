"""
定义Graph当中的Nodes
"""
from typing import Dict,Any
from typing import Annotated, TypedDict
from config.loader import get_config
config = get_config()
from langchain.agents.middleware.types import JumpTo, ResponseT, OmitFromInput, PrivateStateAttr
from langchain_core.messages import AnyMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.channels import EphemeralValue

from langgraph.graph import add_messages


major_agent_llm = ChatDeepSeek(model="deepseek-chat",api_key=config.llm.api_key)
get_user_info_llm = ChatDeepSeek(model="deepseek-chat",api_key=config.llm.api_key)

def custom_reducer(current_value: Dict[str, Any], new_value: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个字典，新值会覆盖旧值，但保留旧值中不存在的键"""
    result = current_value.copy()
    result.update(new_value)
    return result


class AgentState(TypedDict):
    """State schema for the agent."""

    messages: Annotated[list[AnyMessage], add_messages]
    jump_to: Annotated[JumpTo | None, EphemeralValue, PrivateStateAttr]
    structured_response: Annotated[ResponseT, OmitFromInput]
    user_info: Annotated[dict,custom_reducer]

def major_agent_node(state:AgentState):
    """
    主Agent节点，下发任务，给到下面的agent
    """
    messages = state["messages"]
    res = major_agent_llm.invoke(messages)





