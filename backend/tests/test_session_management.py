import requests
import json
import time

# 测试完整的会话管理流程
print("=== 测试会话管理完整流程 ===")

# 1. 登录已有用户或注册新用户
print("\n1. 测试用户登录")
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "username": "new_test_user",
    "password": "new_test_password"
}
login_response = requests.post(login_url, json=login_data)
print(f"登录状态码: {login_response.status_code}")
print(f"登录响应: {login_response.text}")

# 如果登录成功，继续测试
if login_response.status_code == 200:
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 2. 测试创建会话
        print("\n2. 测试创建会话")
        create_session_url = "http://localhost:8000/api/sessions"
        create_session_data = {"title": "测试会话 - " + str(int(time.time()))}
        create_session_response = requests.post(create_session_url, json=create_session_data, headers=headers)
        print(f"创建会话状态码: {create_session_response.status_code}")
        print(f"创建会话响应: {create_session_response.text}")
        
        if create_session_response.status_code == 200:
            session_data = create_session_response.json()
            session_id = session_data.get("id")
            
            if session_id:
                # 3. 测试获取会话列表
                print("\n3. 测试获取会话列表")
                get_sessions_url = "http://localhost:8000/api/sessions"
                get_sessions_response = requests.get(get_sessions_url, headers=headers)
                print(f"获取会话列表状态码: {get_sessions_response.status_code}")
                print(f"获取会话列表响应: {get_sessions_response.text}")
                
                # 4. 测试发送消息
                print("\n4. 测试发送消息")
                send_message_url = f"http://localhost:8000/api/sessions/{session_id}/messages"
                message_data = {
                    "text": "测试消息 - " + str(int(time.time())),
                    "sender": "user"
                }
                send_message_response = requests.post(send_message_url, json=message_data, headers=headers)
                print(f"发送消息状态码: {send_message_response.status_code}")
                print(f"发送消息响应: {send_message_response.text}")
                
                # 5. 测试获取会话消息
                print("\n5. 测试获取会话消息")
                get_messages_url = f"http://localhost:8000/api/sessions/{session_id}/messages"
                get_messages_response = requests.get(get_messages_url, headers=headers)
                print(f"获取会话消息状态码: {get_messages_response.status_code}")
                print(f"获取会话消息响应: {get_messages_response.text}")
                
                # 6. 测试获取特定会话
                print("\n6. 测试获取特定会话")
                get_session_url = f"http://localhost:8000/api/sessions/{session_id}"
                get_session_response = requests.get(get_session_url, headers=headers)
                print(f"获取特定会话状态码: {get_session_response.status_code}")
                print(f"获取特定会话响应: {get_session_response.text}")
                
                # 7. 测试更新会话
                print("\n7. 测试更新会话")
                update_session_url = f"http://localhost:8000/api/sessions/{session_id}"
                update_session_data = {"title": "更新后的测试会话 - " + str(int(time.time()))}
                update_session_response = requests.put(update_session_url, json=update_session_data, headers=headers)
                print(f"更新会话状态码: {update_session_response.status_code}")
                print(f"更新会话响应: {update_session_response.text}")

print("\n=== 测试完成 ===")
