from typing import Literal

from langgraph.constants import START
from langgraph.graph import StateGraph, END
from state import OverAllState, RAGState, TavilyState, MixProcessState, OutputState
import node

#  创建 StateGraph实例
builder = StateGraph(OverAllState)

#  注册节点
#  长期记忆导入节点
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
#  结束汇总节点
builder.add_node("finish_node",node.finish, defer = True)


# 条件边的路由函数
def route_condition(state: OverAllState) -> Literal["mix", "rag", "tavily"]:
   """根据value值决定路由到哪个节点"""
   if state["rag_use"]  == True and state["tavily_use"] == True:
      return "mix" # 偶数路由到节点B
   elif state["rag_use"] == True and state["tavily_use"] == False:
      return "rag" # 奇数路由到节点C
   else:
       return "tavily"


def rag_subgraph():
   """rag检索的子图"""
   rag_subgraph_builder = StateGraph(RAGState)
   rag_subgraph_builder.add_node("rag_temp_node", node.rag_temp)
   rag_subgraph_builder.add_edge(START, "rag_temp_node")
   rag_subgraph_builder.add_edge("rag_temp_node",END)
   return rag_subgraph_builder.compile()

def tavily_subgraph():
   """tavily检索的子图"""
   tavily_subgraph_builder = StateGraph(TavilyState)
   tavily_subgraph_builder.add_node("tavily_temp_node", node.tavily_temp)
   tavily_subgraph_builder.add_edge(START, "tavily_temp_node")
   tavily_subgraph_builder.add_edge("tavily_temp_node",END)
   return tavily_subgraph_builder.compile()

def mix_process_subgraph(rag_subgraph, tavily_subgraph):
   """rag&tavily混合检索的子图"""
   mix_process_subgraph_builder = StateGraph(MixProcessState)
   mix_process_subgraph_builder.add_node("rag_temp_node", rag_subgraph)
   mix_process_subgraph_builder.add_node("tavily_temp_node", tavily_subgraph)
   mix_process_subgraph_builder.add_node("mix_temp_node", node.mix_temp,defer = True)
   mix_process_subgraph_builder.add_edge(START, "rag_temp_node")
   mix_process_subgraph_builder.add_edge(START, "tavily_temp_node")
   mix_process_subgraph_builder.add_edge("rag_temp_node","mix_temp_node")
   mix_process_subgraph_builder.add_edge("tavily_temp_node","mix_temp_node")
   mix_process_subgraph_builder.add_edge("mix_temp_node",END)
   return mix_process_subgraph_builder.compile()

def output_process_subgraph():
   """后续输出功能子图"""
   output_process_builder = StateGraph(OutputState)
   output_process_builder.add_node("rag_temp_node", node.rag_temp)
   output_process_builder.add_edge(START, "rag_temp_node")
   output_process_builder.add_edge("rag_temp_node",END)
   return output_process_builder.compile()

def main_graph(rag_subgraph, tavily_subgraph,mix_process_subgraph,output_process_subgraph):
   # 将子图注册为节点
   builder.add_node("rag_subgraph", rag_subgraph)
   builder.add_node("tavily_subgraph", tavily_subgraph)
   builder.add_node("mix_process_subgraph", mix_process_subgraph)
   builder.add_node("output_process_subgraph", output_process_subgraph)

   builder.add_edge(START,"long_term_memory_import")
   builder.add_edge(START,"title_generate")
   builder.add_edge("long_term_memory_import","intention_recognition")
   builder.add_edge("title_generate","convergence_node")
   builder.add_edge("intention_recognition","convergence_node")
   builder.add_conditional_edges(
      "convergence_node",
      route_condition,
      {
         "mix": "mix_process_subgraph",
         "tavily": "tavily_subgraph",
         "rag": "rag_subgraph"
      }
   )
   builder.add_edge("mix_process_subgraph","llm_response")
   builder.add_edge("tavily_subgraph","llm_response")
   builder.add_edge("rag_subgraph","llm_response")
   builder.add_edge("llm_response","memory_summary")
   builder.add_edge("llm_response","output_process_subgraph")
   builder.add_edge("output_process_subgraph","finish_node")
   builder.add_edge("memory_summary","finish_node")
   builder.add_edge("finish_node",END)
   return builder.compile()

#  创建所有子图实例
rag_sub = rag_subgraph()
tavily_sub = tavily_subgraph()
mix_sub = mix_process_subgraph(rag_sub, tavily_sub)
output_sub = output_process_subgraph()

graph = main_graph(rag_sub, tavily_sub,mix_sub,output_sub)
graph.invoke
