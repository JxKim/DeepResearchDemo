from typing import TypedDict, List, Tuple


class OverAllState(TypedDict):
   user_id: str   #用户ID
   session_id: str   #会话ID
   conversation_history: List[Tuple[str, str]]  #短期会话记忆
   original_query: str  #原始查询

   # 会话标题节点生成
   conversation_title:str  #会话标题

   # 长期记忆导入节点生成
   memory_summary:List[str]   #长期记忆摘要

   # 意图识别节点
   rag_use:bool   #是否使用RAG
   tavily_use:bool   #是否使用Tavily

   # 生成最终回答节点
   final_answer:str  #最终回答

   rag_temp_str:str  #RAG模板字符串


# RAG检索子图状态
class RAGState(TypedDict):
   rag_temp_str:str  #RAG模板字符串

# Tavily搜索子图节点  
class TavilyState(TypedDict):
   tavily_temp_str:str  #Tavily模板字符串

#RAG & Tavliy 混合搜索子图节点
class MixProcessState(RAGState, TavilyState):
   pass  #继承父类

# 后续输出功能子图
class OutputState(TypedDict):
   output_temp_str:str  #后续输出功能子图