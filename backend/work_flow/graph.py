from typing import Literal

from langgraph.constants import START
from langgraph.graph import StateGraph, END
from state import OverAllState
import node

#  创建 StateGraph实例
builder = StateGraph(OverAllState)

#  注册节点
#  记忆导入节点
builder.add_node("long_term_memory_import", node.long_term_memory_import)
#  标题生成节点
builder.add_node("title_generate", node.title_generate)
#  意图识别节点
builder.add_node("intention_recognition", node.intention_recognition)
#  汇合节点
builder.add_node("convergence_node", node.convergence_node, defer = True)
#  llm生成回答节点
builder.add_node("llm_response", node.llm_response)
#  总结记忆节点
builder.add_node("memory_summary", node.memory_summary)
#  rag检索节点
builder.add_node("rag_process",node.rag_process)
#  tavily检索节点
builder.add_node("tavily_process",node.tavily_process)
#  混合检索节点
builder.add_node("mix_process",node.mix_process)

# 条件边的路由函数
def route_condition(state: OverAllState) -> Literal["mix", "rag", "tavily"]:
   """根据value值决定路由到哪个节点"""
   if state["rag_use"]  == True and state["tavily_use"] == True:
      return "mix" # 偶数路由到节点B
   elif state["rag_use"] == True and state["tavily_use"] == False:
      return "rag" # 奇数路由到节点C
   else:
       return "tavily"

def main_graph():

   builder.add_edge(START,"long_term_memory_import")
   builder.add_edge(START,"title_generate")
   builder.add_edge("long_term_memory_import","intention_recognition")
   builder.add_edge("title_generate","convergence_node")
   builder.add_edge("intention_recognition","convergence_node")
   builder.add_conditional_edges(
      "convergence_node",
      route_condition,
      {
         "mix": "mix_process",
         "tavily": "tavily_process",
         "rag": "rag_process"
      }
   )
   builder.add_edge("mix_process","llm_response")
   builder.add_edge("tavily_process","llm_response")
   builder.add_edge("rag_process","llm_response")
   builder.add_edge("llm_response","memory_summary")
   builder.add_edge("memory_summary",END)
   return builder.compile()

graph = main_graph()
graph.invoke
