import React, { useState, useEffect } from 'react';
import api from './api';
import ReactMarkdown from 'react-markdown';
import './App.css';
import Login from './components/Login';

function App() {
  // 用户认证状态
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  
  // 聊天历史记录状态
  const [chatHistory, setChatHistory] = useState([]);
  
  // 当前聊天记录状态
  const [currentChat, setCurrentChat] = useState([]);
  
  // 当前选中的会话ID
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  
  // 新消息输入状态
  const [newMessage, setNewMessage] = useState('');
  
  // 函数调用弹窗状态
  const [showFuncCallModal, setShowFuncCallModal] = useState(false);
  const [currentFuncCall, setCurrentFuncCall] = useState(null);
  
  // 跟踪哪些AI消息的tool_messages是展开的
  const [expandedToolMessages, setExpandedToolMessages] = useState({});

  // 获取聊天会话历史
  const fetchChatSessions = async () => {
    try {
      const response = await api.get('/sessions');
      // 会话列表在response.data.data中
      const sessions = response.data.data || [];
      setChatHistory(sessions);
      
      // 如果有会话，默认选择第一个
      if (sessions.length > 0 && !selectedSessionId) {
        handleSelectSession(sessions[0].id);
      }
    } catch (error) {
      console.error('获取聊天会话失败:', error);
    }
  };

  // 获取特定会话的消息
  const fetchSessionMessages = async (sessionId) => {
    try {
      const response = await api.get(`/sessions/${sessionId}/messages`);
      setCurrentChat(response.data);
    } catch (error) {
      console.error('获取会话消息失败:', error);
    }
  };

  // 处理选择会话
  const handleSelectSession = async (sessionId) => {
    setSelectedSessionId(sessionId);
    await fetchSessionMessages(sessionId);
  };

  // 发送新消息
  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedSessionId) return;

    try {
      // 先将用户消息添加到本地聊天记录
      const userMessage = {
        id: Date.now().toString(),
        text: newMessage,
        sender: 'user',
        timestamp: new Date().toISOString()
      };
      setCurrentChat(prev => [...prev, userMessage]);
      
      // 更新会话列表中的最后消息
      setChatHistory(prev => prev.map(session => 
        session.id === selectedSessionId 
          ? { ...session, lastMessage: newMessage, timestamp: new Date().toLocaleTimeString('zh-CN', { 
              hour: '2-digit', 
              minute: '2-digit', 
              second: '2-digit' 
            }) }
          : session
      ));
      
      // 清空输入框
      setNewMessage('');
      
      // 创建一个临时ID用于AI回复
      const aiMessageId = `ai-${Date.now()}`;
      
      // 添加一个空的AI消息占位符，使用sections数组存储所有消息段落（ai_message和tool_message）
      setCurrentChat(prev => [...prev, {
        id: aiMessageId,
        sections: [], // 存储所有消息段落，每个段落包含type和content
        sender: 'agent',
        timestamp: new Date().toISOString(),
        tool_messages: [] // 兼容旧格式
      }]);
      
      // 使用fetch API直接处理流式响应，不使用axios
      const response = await fetch(`http://localhost:8000/api/sessions/${selectedSessionId}/messages/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          text: newMessage,
          metadata: {},
          sender: 'user'
        }),
        // credentials: 'include', // 发送凭据，处理CORS
        // mode: 'cors' // 显式设置为cors模式
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // 处理流式响应
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // 解码新的字节
        buffer += decoder.decode(value, { stream: true });
        
        // 处理每一行SSE数据
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 保留最后一行不完整的数据
        
        let stopStreaming = false;
        
        for (const line of lines) {
          if (stopStreaming) break;
          
          if (line.trim().startsWith('data :')) {
            // 解析SSE数据行，格式：data : {"ai_message": "内容"} 或 {"func_call": {"to": "...", "subject": "...", "body": "..."}}
            try {
              const jsonStr = line.trim().slice(7); // 去掉 "data : " 前缀
              const data = JSON.parse(jsonStr);
              
              if (data.ai_message) {
                // 更新accumulatedText变量
                accumulatedText += data.ai_message;
                
                // 只在消息不重复时添加内容
                setCurrentChat(prev => prev.map(msg => {
                  if (msg.id === aiMessageId) {
                    const updatedSections = [...msg.sections];
                    let lastSection = updatedSections[updatedSections.length - 1];
                    
                    if (lastSection && lastSection.type === 'ai_message') {
                      // 检查当前消息片段是否已经包含在现有内容中，避免重复
                      if (!lastSection.content.includes(data.ai_message)) {
                        lastSection.content += data.ai_message;
                      }
                    } else {
                      // 否则创建一个新的ai_message section
                      updatedSections.push({ type: 'ai_message', content: data.ai_message });
                    }
                    
                    return { ...msg, sections: updatedSections };
                  }
                  return msg;
                }));
              } else if (data.tool_message) {
                // 将tool_message添加到sections数组中
                setCurrentChat(prev => prev.map(msg => 
                  msg.id === aiMessageId 
                    ? { 
                        ...msg, 
                        sections: [...msg.sections, { type: 'tool_message', content: data.tool_message }] 
                      }
                    : msg
                ));
              } else if (data.func_call && typeof data.func_call === 'object') {
                // 检测到函数调用请求，显示弹窗
                setCurrentFuncCall(data.func_call);
                setShowFuncCallModal(true);
                
                // 停止当前流式响应处理，因为后续响应会由handleToolCall处理
                stopStreaming = true;
                break;
              }
            } catch (error) {
              console.error('解析SSE数据失败:', error);
              // 继续处理下一行，避免整个应用崩溃
            }
          }
        }
        
        if (stopStreaming) {
          // 停止流式响应处理
          await reader.cancel();
          break;
        }
      }
      
      // 流式响应结束后，更新会话列表中的最后消息
      setChatHistory(prev => prev.map(session => 
        session.id === selectedSessionId 
          ? { ...session, lastMessage: accumulatedText, timestamp: new Date().toLocaleTimeString('zh-CN', { 
              hour: '2-digit', 
              minute: '2-digit', 
              second: '2-digit' 
            }) }
          : session
      ));
    } catch (error) {
      console.error('发送消息失败:', error);
      // 可以添加错误处理，比如显示错误消息
    }
  };

  // 处理工具调用请求
  const handleToolCall = async (isAuthorized) => {
    if (!selectedSessionId || !currentFuncCall) return;

    try {
      // 调用后端工具调用接口
      const response = await fetch(`http://localhost:8000/api/sessions/${selectedSessionId}/messages/tools`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          tool_name: 'send_email',
          parameters: currentFuncCall,
          is_authorized: isAuthorized
        }),
        // credentials: 'include', // 发送凭据，处理CORS
        // mode: 'cors' // 显式设置为cors模式
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // 处理流式响应
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      // 找到当前AI消息，用于更新sections字段
      const aiMessages = currentChat.filter(msg => msg.sender === 'agent');
      const lastAiMessageId = aiMessages[aiMessages.length - 1]?.id;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // 解码新的字节
        buffer += decoder.decode(value, { stream: true });
        
        // 按行分割数据
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 保留最后一行不完整的数据
        
        for (const line of lines) {
          if (line.trim().startsWith('data :')) {
            // 解析SSE数据行
            try {
              const jsonStr = line.trim().slice(7); // 去掉 "data : " 前缀
              const data = JSON.parse(jsonStr);
              
              if (data.ai_message) {
                // 只在消息不重复时添加内容
                if (lastAiMessageId) {
                  setCurrentChat(prev => prev.map(msg => {
                    if (msg.id === lastAiMessageId) {
                      const updatedSections = [...msg.sections];
                      let lastSection = updatedSections[updatedSections.length - 1];
                       
                      if (lastSection && lastSection.type === 'ai_message') {
                        // 检查当前消息片段是否已经包含在现有内容中，避免重复
                        if (!lastSection.content.includes(data.ai_message)) {
                          lastSection.content += data.ai_message;
                        }
                      } else {
                        // 否则创建一个新的ai_message section
                        updatedSections.push({ type: 'ai_message', content: data.ai_message });
                      }
                       
                      return { ...msg, sections: updatedSections };
                    }
                    return msg;
                  }));
                }
              } else if (data.tool_message) {
                // 将tool_message添加到sections数组中
                if (lastAiMessageId) {
                  setCurrentChat(prev => prev.map(msg => 
                    msg.id === lastAiMessageId 
                      ? { 
                          ...msg, 
                          sections: [...msg.sections, { type: 'tool_message', content: data.tool_message }] 
                        }
                      : msg
                  ));
                }
              }
            } catch (error) {
              console.error('解析SSE数据失败:', error);
              // 继续处理下一行，避免整个应用崩溃
            }
          }
        }
      }
      
      // 流式响应结束后，更新会话列表中的最后消息
      // 找到当前AI消息，提取最后一个ai_message作为会话的最后消息
      setChatHistory(prev => {
        // 从当前聊天记录中找到最后一条AI消息
        const currentAI = currentChat.filter(msg => msg.sender === 'agent').pop();
        let lastMessage = '';
        if (currentAI) {
          if (currentAI.sections && currentAI.sections.length > 0) {
            // 找到最后一个ai_message
            const lastAiSection = currentAI.sections.filter(section => section.type === 'ai_message').pop();
            if (lastAiSection) {
              lastMessage = lastAiSection.content;
            }
          } else if (currentAI.text) {
            // 兼容旧格式的AI消息
            lastMessage = currentAI.text;
          }
        }
        
        return prev.map(session => 
          session.id === selectedSessionId 
            ? { ...session, lastMessage: lastMessage, timestamp: new Date().toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
              }) }
            : session
        );
      });
    } catch (error) {
      console.error('处理工具调用失败:', error);
    }
  };

  // 创建新会话
  const handleCreateSession = async () => {
    try {
      const response = await api.post('/sessions', {
        title: `新会话 ${chatHistory.length + 1}`
      });
      
      // 更新会话列表，将新会话添加到开头
      const newSession = response.data;
      setChatHistory(prev => [newSession, ...prev]);
      
      // 选择新创建的会话
      handleSelectSession(newSession.id);
    } catch (error) {
      console.error('创建会话失败:', error);
      // 打印完整的错误信息，方便调试
      if (error.response) {
        console.error('响应状态:', error.response.status);
        console.error('响应数据:', error.response.data);
      } else if (error.request) {
        console.error('请求:', error.request);
      } else {
        console.error('请求错误:', error.message);
      }
    }
  };

  // 用户认证相关函数
  const handleLogin = (userData) => {
    setUser(userData);
    // 登录成功后，立即获取会话列表
    fetchChatSessions();
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setChatHistory([]);
    setCurrentChat([]);
    setSelectedSessionId(null);
  };

  // 组件挂载时获取初始数据和检查登录状态
  useEffect(() => {
    // 检查本地存储中是否有用户信息
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        // 如果用户已登录，获取会话列表
        fetchChatSessions();
      } catch (error) {
        console.error('解析用户信息失败:', error);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
  }, []); // 空依赖数组，只在组件挂载时执行一次

  // 选择会话时加载消息，不需要轮询
  useEffect(() => {
    if (selectedSessionId) {
      fetchSessionMessages(selectedSessionId);
    }
  }, [selectedSessionId]); // 当选中的会话ID变化时，一次性加载消息

  // 处理键盘事件
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };
  
  // 处理tool_messages的展开/折叠
  const toggleToolMessages = (messageId) => {
    setExpandedToolMessages(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  return (
    <div className="app-container">
      <div className="chat-layout">
        {/* 左侧聊天历史记录 */}
        <div className="chat-history">
          <div className="history-header">
            <h2>聊天历史</h2>
            <button onClick={handleCreateSession} className="new-session-btn">新建会话</button>
          </div>
          <div className="history-list">
            {chatHistory.map(chat => (
              <div 
                key={chat.id} 
                className={`history-item ${selectedSessionId === chat.id ? 'active' : ''}`}
                onClick={() => handleSelectSession(chat.id)}
              >
                <div className="history-title">{chat.title}</div>
                <div className="history-preview">{chat.lastMessage}</div>
                <div className="history-time">{chat.timestamp}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧当前聊天窗口 */}
        <div className="chat-window">
          <div className="chat-header">
            <h2>{chatHistory.find(s => s.id === selectedSessionId)?.title || '请选择会话'}</h2>
            <div className="user-info">
              {user ? (
                <div className="user-menu">
                  <span className="username">欢迎，{user.username}</span>
                  <button onClick={handleLogout} className="logout-btn">登出</button>
                </div>
              ) : (
                <button 
                  onClick={() => setShowLogin(true)} 
                  className="login-btn"
                >
                  登录
                </button>
              )}
            </div>
          </div>
          <div className="chat-messages">
            {currentChat.map(message => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-text">
                  {message.sender === 'agent' ? (
                    <>
                      {/* 按照sections数组的顺序渲染每个消息段落 */}
                      {message.sections && message.sections.length > 0 ? (
                        message.sections.map((section, index) => (
                          <React.Fragment key={`${message.id}-${section.type}-${index}`}>
                            {section.type === 'ai_message' ? (
                              /* 渲染AI消息文本 */
                              <ReactMarkdown>{section.content}</ReactMarkdown>
                            ) : (section.type === 'tool_message' && (
                              /* 渲染可折叠的工具消息，每个工具消息一个独立窗口 */
                              <div className="tool-messages-container">
                                <button 
                                  className="tool-messages-toggle"
                                  onClick={() => toggleToolMessages(`${message.id}-tool-${index}`)}
                                >
                                  {expandedToolMessages[`${message.id}-tool-${index}`] ? '▼ 收起工具消息' : '▶ 查看工具消息'}
                                </button>
                                {expandedToolMessages[`${message.id}-tool-${index}`] && (
                                  <div className="tool-messages-content">
                                    <div className="tool-message">
                                      <pre>{JSON.stringify(section.content, null, 2)}</pre>
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </React.Fragment>
                        ))
                      ) : (
                        /* 兼容旧格式的AI消息 */
                        <ReactMarkdown>{message.text || ''}</ReactMarkdown>
                      )}
                    </>
                  ) : (
                    message.text
                  )}
                </div>
                <div className="message-time">
                  {message.timestamp ? new Date(message.timestamp).toLocaleTimeString('zh-CN', { 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit' 
                  }) : ''}
                </div>
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input 
              type="text" 
              placeholder={selectedSessionId ? "输入消息..." : "请先选择一个会话"} 
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!selectedSessionId}
            />
            <button onClick={handleSendMessage} disabled={!selectedSessionId}>发送</button>
          </div>
        </div>
      </div>

      {/* 登录模态框 */}
      {showLogin && (
        <Login 
          onLogin={handleLogin}
          onClose={() => setShowLogin(false)}
        />
      )}
      
      {/* 函数调用确认弹窗 */}
      {showFuncCallModal && currentFuncCall && typeof currentFuncCall === 'object' && (
        <div className="func-call-modal-overlay">
          <div className="func-call-modal">
            <h3>函数调用请求</h3>
            <div className="func-call-content">
              <p>AI请求调用以下函数：</p>
              <div className="func-call-details">
                <p><strong>函数名称：</strong>send_email</p>
                <p><strong>参数：</strong></p>
                <ul>
                  {Object.entries(currentFuncCall).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}：</strong>{typeof value === 'string' ? value : JSON.stringify(value)}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="func-call-buttons">
              <button className="func-call-approve" onClick={async () => {
                // 同意按钮点击事件
                setShowFuncCallModal(false);
                await handleToolCall(true);
              }}>同意</button>
              <button className="func-call-reject" onClick={async () => {
                // 拒绝按钮点击事件
                setShowFuncCallModal(false);
                await handleToolCall(false);
              }}>拒绝</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
