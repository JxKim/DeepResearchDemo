#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档写入demo

使用说明：
1. 请先在飞书开发者平台创建应用，获取App ID和App Secret
2. 确保应用已获得文档相关权限（如：docs:doc:write, docs:document:read_write）
3. 替换下方的APP_ID、APP_SECRET和DOCUMENT_ID为实际值
"""

import requests
import json

# 飞书应用配置
APP_ID = "cli_a9a681ebdafb9bc9"  # 替换为你的App ID
APP_SECRET = "3nlrxGhZtFPLQWIQC91iQXZovqZXYB6k"  # 替换为你的App Secret
DOCUMENT_ID = "S0e0d81EioQvISxLcbkc4sldnlf"  # 替换为你的飞书文档ID
MARKDOWN_CONTENT="""
# SmartAgent API 文档

## 技术栈
- FastAPI
- Uvicorn
- Python 3.8+

## 基础URL
```
http://localhost:8000
```

## API 端点

### 1. 用户认证与权限管理

#### 用户注册
- **URL**: `POST /api/auth/register`
- **描述**: 用户注册
- **请求体**:
  ```json
  {
    "username": "用户名",
    "email": "邮箱",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "id": "用户ID",
    "username": "用户名",
    "email": "邮箱",
    "created_at": "注册时间"
  }
  ```

#### 用户登录
- **URL**: `POST /api/auth/login`
- **描述**: 用户登录
- **请求体**:
  ```json
  {
    "username": "用户名",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "JWT访问令牌",
    "token_type": "bearer",
    "user": {
      "id": "用户ID",
      "username": "用户名",
      "email": "邮箱"
    }
  }
  ```

#### 用户登出
- **URL**: `POST /api/auth/logout`
- **描述**: 用户登出
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  {
    "message": "登出成功"
  }
  ```

### 2. 会话管理

#### 创建新会话
- **URL**: `POST /api/sessions/`
- **描述**: 创建一个新的聊天会话
- **请求头**: `Authorization: Bearer {token}`
- **请求体**:
  ```json
  {
    "title": "会话标题（可选）"
  }
  ```
- **响应**:
  ```json
  {
    "id": "会话ID",
    "title": "会话标题",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "messages": []
  }
  ```

#### 获取所有会话
- **URL**: `GET /api/sessions/`
- **描述**: 获取当前用户的所有聊天会话列表
- **请求头**: `Authorization: Bearer {token}`
- **响应**:
  ```json
  [
    {
      "id": "会话ID",
      "title": "会话标题",
      "last_message": "最后一条消息内容",
      "timestamp": "最后更新时间"
    }
  ]
  ```

#### 获取特定会话
- **URL**: `GET /api/sessions/{session_id}`
- **描述**: 获取特定会话的详细信息
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **响应**:
  ```json
  {
    "id": "会话ID",
    "title": "会话标题",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "messages": [
      {
        "id": "消息ID",
        "text": "消息内容",
        "sender": "发送者(user/agent)",
        "timestamp": "消息时间"
      }
    ]
  }
  ```

#### 删除会话
- **URL**: `DELETE /api/sessions/{session_id}`
- **描述**: 删除指定会话
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **响应**:
  ```json
  {
    "message": "会话删除成功"
  }
  ```

### 3. 消息管理

#### 添加消息到会话
- **URL**: `POST /api/sessions/{session_id}/messages/`
- **描述**: 向指定会话添加一条新消息
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **请求体**:
  ```json
  {
    "text": "消息内容",
    "sender": "发送者(user/agent)"
  }
  ```
- **响应**:
  ```json
  {
    "id": "消息ID",
    "text": "消息内容",
    "sender": "发送者",
    "timestamp": "消息时间"
  }
  ```

#### 获取会话中的消息（分页加载）
- **URL**: `GET /api/sessions/{session_id}/messages/`
- **描述**: 获取指定会话中的消息，支持分页加载
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `session_id`: 会话ID（路径参数）
  - `page`: 页码（可选，默认1）
  - `page_size`: 每页消息数量（可选，默认20）
  - `before_message_id`: 在此消息ID之前加载（可选，用于无限滚动）
  - `limit`: 限制返回的消息数量（可选）
- **响应**:
  ```json
  {
    "messages": [
      {
        "id": "消息ID",
        "text": "消息内容",
        "sender": "发送者(user/agent)",
        "timestamp": "消息时间",
        "type": "text|tool_request|tool_result"
      }
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_messages": 150,
      "total_pages": 8,
      "has_previous": false,
      "has_next": true,
      "next_page_token": "eyJwYWdlIjoyLCJzaXplIjoyMH0="
    }
  }
  ```

#### 获取会话消息历史（按时间范围）
- **URL**: `GET /api/sessions/{session_id}/messages/history`
- **描述**: 按时间范围获取会话消息历史，支持无限滚动
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `session_id`: 会话ID（路径参数）
  - `before_timestamp`: 在此时间之前加载消息（可选）
  - `after_timestamp`: 在此时间之后加载消息（可选）
  - `limit`: 限制返回的消息数量（可选，默认50）
  - `direction`: 加载方向（"older" 或 "newer"，默认"older"）
- **响应**:
  ```json
  {
    "messages": [
      {
        "id": "消息ID",
        "text": "消息内容",
        "sender": "发送者(user/agent)",
        "timestamp": "消息时间",
        "type": "text|tool_request|tool_result"
      }
    ],
    "has_more_older": true,
    "has_more_newer": false,
    "oldest_timestamp": "2024-01-01T00:00:00Z",
    "newest_timestamp": "2024-01-15T12:00:00Z",
    "next_older_token": "eyJ0aW1lc3RhbXAiOiIyMDI0LTAxLTAxVDAwOjAwOjAwWiJ9",
    "next_newer_token": null
  }
  ```

#### 删除消息
- **URL**: `DELETE /api/sessions/{session_id}/messages/{message_id}`
- **描述**: 删除指定会话中的特定消息
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
  - `message_id`: 消息ID
- **响应**:
  ```json
  {
    "message": "消息删除成功"
  }
  ```

### 4. 智能Agent处理

#### 发送消息给Agent
- **URL**: `POST /api/sessions/{session_id}/agent/message`
- **描述**: 发送用户消息给Agent处理
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **请求体**:
  ```json
  {
    "text": "用户消息内容",
    "context": "对话上下文（可选）"
  }
  ```
- **响应**:
  ```json
  {
    "id": "消息ID",
    "text": "Agent回复内容",
    "sender": "agent",
    "timestamp": "回复时间",
    "status": "completed"
  }
  ```

#### 获取Agent处理状态
- **URL**: `GET /api/sessions/{session_id}/agent/status`
- **描述**: 获取Agent当前处理状态
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **响应**:
  ```json
  {
    "status": "idle|processing|waiting_authorization|completed",
    "current_action": "当前执行的操作",
    "progress": 0.75
  }
  ```

### 5. 工具调用与授权管理

#### 工具调用请求
- **URL**: `POST /api/sessions/{session_id}/tool-requests`
- **描述**: Agent请求调用某个工具
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **请求体**:
  ```json
  {
    "tool_name": "工具名称",
    "tool_type": "工具类型(file_operation|network_request|system_call)",
    "parameters": {
      "param1": "参数1",
      "param2": "参数2"
    },
    "permission_description": "权限说明",
    "risk_level": "low|medium|high"
  }
  ```
- **响应**:
  ```json
  {
    "request_id": "工具调用请求ID",
    "status": "pending_authorization",
    "tool_name": "工具名称",
    "permission_description": "权限说明",
    "created_at": "请求时间"
  }
  ```

#### 用户授权工具调用
- **URL**: `POST /api/sessions/{session_id}/tool-requests/{request_id}/authorize`
- **描述**: 用户授权或拒绝工具调用
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
  - `request_id`: 工具调用请求ID
- **请求体**:
  ```json
  {
    "authorized": true,
    "authorization_parameters": {
      "scope": "授权范围",
      "duration": "授权时长"
    }
  }
  ```
- **响应**:
  ```json
  {
    "request_id": "工具调用请求ID",
    "status": "authorized|rejected",
    "execution_result": "执行结果（如果授权）",
    "error_message": "错误信息（如果拒绝）"
  }
  ```

#### 查询工具调用状态
- **URL**: `GET /api/sessions/{session_id}/tool-requests/{request_id}`
- **描述**: 查询工具调用的当前状态
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
  - `request_id`: 工具调用请求ID
- **响应**:
  ```json
  {
    "request_id": "工具调用请求ID",
    "status": "pending_authorization|authorized|rejected|executing|completed|failed",
    "tool_name": "工具名称",
    "authorization_status": "授权状态",
    "execution_result": "执行结果",
    "error_message": "错误信息"
  }
  ```

#### 获取工具执行结果
- **URL**: `GET /api/sessions/{session_id}/tool-requests/{request_id}/result`
- **描述**: 获取工具执行的结果数据
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
  - `request_id`: 工具调用请求ID
- **响应**:
  ```json
  {
    "request_id": "工具调用请求ID",
    "execution_result": "执行结果数据",
    "execution_time": "执行时间",
    "status": "completed|failed"
  }
  ```

### 6. 对话状态管理

#### 暂停对话
- **URL**: `POST /api/sessions/{session_id}/pause`
- **描述**: 暂停当前对话（等待用户操作）
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **响应**:
  ```json
  {
    "status": "paused",
    "reason": "暂停原因",
    "waiting_for": "等待用户操作"
  }
  ```

#### 恢复对话
- **URL**: `POST /api/sessions/{session_id}/resume`
- **描述**: 恢复暂停的对话
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **请求体**:
  ```json
  {
    "user_action": "用户操作结果",
    "context": "恢复上下文"
  }
  ```
- **响应**:
  ```json
  {
    "status": "resumed",
    "next_action": "下一步操作"
  }
  ```

#### 获取对话状态
- **URL**: `GET /api/sessions/{session_id}/status`
- **描述**: 获取当前对话的状态
- **请求头**: `Authorization: Bearer {token}`
- **参数**:
  - `session_id`: 会话ID
- **响应**:
  ```json
  {
    "status": "active|paused|waiting_authorization|completed",
    "current_action": "当前执行的操作",
    "waiting_for": "等待的用户操作",
    "last_updated": "最后更新时间"
  }
  ```

## WebSocket 连接

### 实时消息推送
- **URL**: `ws://localhost:8000/ws/{session_id}`
- **描述**: 通过WebSocket实现实时消息推送
- **参数**:
  - `session_id`: 会话ID
- **消息格式**:
  ```json
  {
    "type": "message",
    "data": {
      "id": "消息ID",
      "text": "消息内容",
      "sender": "发送者",
      "timestamp": "消息时间"
    }
  }
  ```

## 错误响应格式
```json
{
  "detail": "错误描述"
}
```
"""

def get_tenant_access_token(app_id, app_secret):
    """获取飞书应用的访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    
    if response_data.get("code") == 0:
        return response_data.get("tenant_access_token")
    else:
        raise Exception(f"获取访问令牌失败: {response_data}")


def create_docs(title):
    token = get_tenant_access_token(APP_ID,APP_SECRET)
    print('当前token为：',token)
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    request_body={
        "title":title
    }
    response = requests.post(url, headers=headers, json=request_body)
    print(response.status_code)
    response_json = response.json()
    print(response_json)
    return response_json['data']['document']['document_id']
    # print(response.text)

def convert_to_block(markdown_content):
    """

    """
    request_url = "https://open.feishu.cn/open-apis/docx/v1/documents/blocks/convert?user_id_type=user_id"
    token = get_tenant_access_token(APP_ID,APP_SECRET)
    header={
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    request_body={
        "content_type": "markdown",
        "content": markdown_content
    }
    response = requests.post(request_url, headers=header, json=request_body)
    print(response.status_code)
    return response.json()['data']['first_level_block_ids'],response.json()['data']['blocks']
def write_to_feishu_doc(document_id,first_level_block_ids,blocks):
    """
    将嵌套块，写入到飞书文档当中
    """
    request_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/descendant?document_revision_id=-1"
    token = get_tenant_access_token(APP_ID,APP_SECRET)
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    request_body = {
      "index": 0,
      "children_id": first_level_block_ids,
      "descendants": blocks
    }
    response = requests.post(url=request_url,headers=header,json=request_body)
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    print("开始执行飞书文档写入demo...")
    document_id = create_docs("SmartAPI接口文档")
    first_level_block_ids,blocks = convert_to_block(MARKDOWN_CONTENT)
    write_to_feishu_doc(document_id,first_level_block_ids,blocks)
    print("demo执行完成!")
