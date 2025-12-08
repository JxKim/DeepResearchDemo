from typing import List, Optional
from datetime import datetime

from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tests.models import MessageCreate, Session, SessionStatus
from models.db_models import Session
from services.agent import get_agent
from langchain_core.messages import BaseMessage, ToolMessage

from config.loguru_config import get_logger

logger = get_logger(__name__)

class SessionService:
    """

    """
    def __init__(self):
        self.agent = None
        pass

    async def init_agent(self):
        """初始化agent"""
        if not self.agent:
            self.agent = await get_agent()

    
    async def create_session(self, user_id,title,db: AsyncSession) -> Session:
        """创建新会话"""
        import uuid
        session_id = str(uuid.uuid4())
        db_session = Session(
            id=session_id,
            user_id=user_id,
            title=title,
            conversation_status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            message_count=0
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session
    
    async def get_session(self, session_id: str,db: AsyncSession) -> Optional[Session]:
        """
        使用session_id从数据库中读取单条session会话
        """
        result = await db.execute(select(Session).where(Session.id == session_id))
        db_session = result.scalar_one_or_none()
        if not db_session:
            return None
        return Session(
            id=db_session.id,
            user_id=db_session.user_id,
            title=db_session.title,
            conversation_status=db_session.conversation_status,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
            message_count=db_session.message_count
        )

    async def get_sessions(self,user_id: str,db: AsyncSession) -> list[Session]:
        """获取用户的所有会话（分页）"""
        result = await db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.updated_at.desc())
        )
        db_sessions = result.scalars().all()

        return [
            Session(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                conversation_status=session.conversation_status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=session.message_count
            ) for session in db_sessions
        ]

    async def get_messages(self, session_id: str) -> List[BaseMessage]:
        """
        通过agent获取到消息列表
        """
        await self.init_agent()
        config = {
            "configurable":
                {"thread_id":session_id}
        }
        state_res = await self.agent.aget_state(config=config)

        return state_res.values['messages'] if state_res and state_res.values else []

    async def add_message_to_session(self,session_id: str, user_id: str, message_data: MessageCreate,db: AsyncSession):
        """向会话添加消息"""
        import json
        session = await session_service.get_session(session_id,db)
        if not session or session.user_id != user_id:
            return None

        config = {
            "configurable":
                {"thread_id":session_id}
        }
        await self.init_agent()
        async def generate_response():
            try:
                async for chunk in self.agent.astream(
                    input={"messages":("user",message_data.text)},
                    config=config,
                    stream_mode=["updates","messages"]
                ):
                    if chunk[0] == "messages":
                        # print(type(chunk[1][0]))
                        if isinstance(chunk[1][0], ToolMessage):
                            message_json = {
                                "tool_message": chunk[1][0].content
                            }
                            tool_data = json.dumps(message_json)
                            yield f"data : {tool_data}\n\n"
                        else:
                            if chunk[1][0].content: # 只输出有内容的信息
                                message_json = {
                                    "ai_message": chunk[1][0].content
                                }
                                ai_data = json.dumps(message_json)

                                yield f"data : {ai_data}\n\n"
                            else:
                                continue
                    elif chunk[0] == "updates" and "__interrupt__" in chunk[1]:
                        interrupt_value = chunk[1]["__interrupt__"][0].value
                        interrupt_json = {
                            "func_call": interrupt_value
                        }
                        data = json.dumps(interrupt_json)
                        # yield chunk[1]
                        yield f"data : {data}\n\n"
            except Exception as e:
                logger.error(e)
                raise ServerSideSession(e)


        return generate_response()

    async def tool_invoke(self,session_id,is_approved):
        """
        执行工具调用，
        """
        import json
        config = {
            "configurable":
                {"thread_id": session_id}
        }
        await self.init_agent()
        async def generate_response(command:Command):
            async for chunk in self.agent.astream(
                    input=command,
                    config=config,
                    stream_mode=["updates", "messages"]
            ):
                if chunk[0] == "messages":
                    if isinstance(chunk[1][0], ToolMessage):
                        message_json = {
                            "tool_message": chunk[1][0].content
                        }
                    else:
                        message_json = {
                            "ai_message": chunk[1][0].content
                        }
                    data = json.dumps(message_json)
                    yield f"data : {data}\n\n"
            yield "data : [DONE]\n\n"
        if is_approved:
            # agent继续执行
            return generate_response(Command(resume=True))
        else:
            return generate_response(Command(resume=False))

# 创建单例实例
session_service = SessionService()
