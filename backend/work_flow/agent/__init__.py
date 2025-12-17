from langchain.agents import create_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
from pathlib import Path
from config.loader import get_config
config = get_config()

async def get_agent(system_prompt: str):
    """
    获取Agent实例
    :param system_prompt: 系统提示词，作为参数传入，而非固定
    :return: agent
    """
    from langchain_deepseek import ChatDeepSeek
    from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model=config.llm.model,api_key=config.llm.api_key,base_url=config.llm.base_url)
    llm = ChatDeepSeek(model=config.llm.model,api_key=config.llm.api_key,base_url=config.llm.base_url)
    
    # 确保存储路径存在
    db_path = Path(__file__).parent / "data" / "langgraph_checkpoint"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = await aiosqlite.connect(str(db_path))
    sqlite_saver = AsyncSqliteSaver(
        conn=conn
    )

    agent = create_agent(
        model=llm,
        tools=[],
        checkpointer=sqlite_saver,
        system_prompt=system_prompt # 使用传入的 prompt
    )

    return agent

if __name__ == '__main__':
    pass
