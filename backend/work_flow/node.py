from state import OverAllState, RAGState, MixProcessState


def long_term_memory_import(state: OverAllState) -> dict:
   """
   长期记忆导入节点
   
   Args:
      state: 当前状态
      
   Returns:
      dict: 更新后的状态
   """
   print("执行节点: long_term_memory_import")

   # 从磁盘读取本次会话的长期记忆，并写入状态
   read_summaries = "待实现的获取记忆功能"

   return {"memory_summary": read_summaries}


def title_generate(state: OverAllState) -> dict:
    """
      标题创建

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
      """
    print("执行节点: title_generate")

    # 根据用户原始输入生成标题，并将标题名称进行传输给前端进行显示
    title = "待实现的获取记忆功能"
    return {"conversation_title": title}

def intention_recognition(state: OverAllState) -> dict:
    """
      意图识别

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
      """
    print("执行节点: intention_recognition")

    # 使用llm处理，完成检索意图识别
    # rag_use:bool
    # tavily_use:bool
    rag_use = True
    tavily_use = True
    return {"rag_use": rag_use, "tavily_use": tavily_use}

def convergence_node(state: OverAllState) -> dict:
    """
      汇合节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
      """
    print("执行节点: convergence_node")

    # 等待前序任务完成，继续传递工作流
    rag_use = True
    tavily_use = True
    return {"rag_use": rag_use, "tavily_use": tavily_use}

def llm_response(state: OverAllState) -> dict:
    """
      生成回复节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
    """
    print("执行节点: llm_response")
    final_answer = "最终回答"

    # 结合所有现存语料，构造提示词模板，获取LLM回复
    return{"final_answer":final_answer}

def memory_summary(state: OverAllState) -> dict:
    """
      记忆总结节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
    """
    print("执行节点: memory_summary")
    final_answer = "最终回答"

    # 结合所有现存语料，构造提示词模板，获取LLM回复
    return {"final_answer": final_answer}

def rag_temp(state: RAGState) -> dict:
    """
      rag占位节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
    """
    return {"rag_temp_str": state["rag_temp_str"]}

def tavily_temp(state: RAGState) -> dict:
    """
      tavily占位节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
    """
    return {"tavily_temp_str": state["tavily_temp_str"]}

def mix_temp(state: MixProcessState) -> dict:
    """
      混合检索占位节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
    """
    return {"mix_temp_str": state["mix_temp_str"]}

def finish(state :OverAllState) -> dict:
    """
      汇总结束节点

      Args:
         state: 当前状态

      Returns:
         dict: 更新后的状态
    """
    return
