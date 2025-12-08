from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional

from langchain_core.messages import HumanMessage, AIMessage
from starlette.responses import StreamingResponse

from routes.schema import (
    Session, SessionListItem, Message, MessageCreate,
    SessionListResponse, User, SenderType, ToolRequestResponse, ToolInvokeRequest, SessionCreate
)
# from controllers.auth_controller import verify_token
from services.session_service import session_service
from services.auth_service import auth_service
from config.loguru_config import get_logger

from database import get_db,SessionLocal
logger = get_logger(__name__)
# 依赖函数：从请求头中获取并验证令牌
async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> User:
    """从请求头中获取并验证令牌，返回当前用户"""
    from database import SessionLocal
    logger.info('get_current_user_from_token 被调用')
    
    if not authorization:
        logger.info('未提供授权令牌')
        raise HTTPException(status_code=401, detail="未提供授权令牌")
    
    # 提取令牌（移除Bearer前缀）
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        logger.info(f'提取到的令牌: {token}')
    else:
        token = authorization
        logger.info(f'提取到的令牌（无Bearer前缀）: {token}')
    
    # 验证令牌
    logger.info('开始验证令牌')
    session = SessionLocal()
    try:
        user = await auth_service.verify_token(token,session)
        if not user:
            logger.info('无效的令牌')
            raise HTTPException(status_code=401, detail="无效的令牌")

        logger.info(f'令牌验证成功，返回用户: {user.id}')
    finally:
        await session.close()
    return user

router = APIRouter(prefix="/sessions", tags=["会话管理"])

@router.post("/", response_model=Session)
async def create_new_session(session_create:SessionCreate,current_user: User = Depends(get_current_user_from_token),db=Depends(get_db)):
    """创建新会话"""
    return await session_service.create_session(current_user.id,session_create.title,db=db)

@router.get("/", response_model=SessionListResponse)
async def list_sessions(current_user: User = Depends(get_current_user_from_token),db=Depends(get_db)):
    """获取所有会话"""
    sessions = await session_service.get_sessions(current_user.id,db=db)
    session_list=[]
    for session in sessions:
        session_list.append(SessionListItem(
            id=session.id,
            title=session.title,
            last_message=None,
            last_message_time=None,
            message_count=0,
            conversation_status=session.conversation_status,
            created_at=session.created_at
        ))
    return SessionListResponse(data=session_list)

@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str, current_user: User = Depends(get_current_user_from_token),db=Depends(get_db)):
    """获取特定会话"""
    session = await session_service.get_session(session_id,db=db)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    return session

@router.post("/{session_id}/messages/", response_model=Message)
async def add_message(session_id: str, message_data: MessageCreate, current_user: User = Depends(get_current_user_from_token),db=Depends(get_db)):
    """当用户输入消息时，添加消息到会话，agent回复用户消息"""
    message_generator = await session_service.add_message_to_session(session_id, current_user.id, message_data,db=db)
    if not message_generator:
        raise HTTPException(status_code=404, detail="会话未找到")
    return StreamingResponse(message_generator,media_type="text/event-stream",)

@router.get("/{session_id}/messages/", response_model=List[Message])
async def get_messages(session_id: str, current_user: User = Depends(get_current_user_from_token)):
    """获取会话中的所有消息"""
    messages = await session_service.get_messages(session_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="会话未找到")
    message_list = []
    for message in messages:
        if type(message) not in (HumanMessage, AIMessage):
            continue
        message_list.append(
            Message(
                id=message.id,
                session_id=session_id,
                sender=SenderType.USER if type(message)==HumanMessage else SenderType.AGENT,
                timestamp=None,
                text=message.content if message.content else ' ',
                metadata=message.response_metadata
            )
        )
    return message_list

@router.post("/{session_id}/messages/tools/", response_model=List[ToolRequestResponse])
async def tool_invoke(session_id:str,tool_invoke_request: ToolInvokeRequest,current_user: User = Depends(get_current_user_from_token)):
    """
    agent调用工具时，发起请求，是否需要获取用户允许，当用户允许时，继续执行工具调用
    否则不进行具体调用
    """
    stream_generator = await session_service.tool_invoke(session_id=session_id,is_approved=tool_invoke_request.is_authorized)
    return StreamingResponse(stream_generator,media_type="text/event-stream",)