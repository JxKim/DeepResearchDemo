from langchain.agents import create_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
from services.agent.tools import send_email, save_report_to_lark, search_web, get_current_datetime
from pathlib import Path
from services.agent.prompts import major_agent_prompt
from config.loader import get_config
config = get_config()

async def get_agent():
    from langchain_deepseek import ChatDeepSeek
    llm = ChatDeepSeek(model="deepseek-chat",api_key=config.llm.api_key)
    conn = await aiosqlite.connect(str(Path(__file__).parent / "data" / "langgraph_checkpoint"))
    sqlite_saver = AsyncSqliteSaver(
        conn=conn
    )
    agent = create_agent(
        model=llm,
        tools=[save_report_to_lark,search_web,send_email,get_current_datetime], # 测试人机协作能力是否能够正常进行
        checkpointer=sqlite_saver,
        system_prompt=major_agent_prompt
    )

    return agent

if __name__ == '__main__':
    pass

