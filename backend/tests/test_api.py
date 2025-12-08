import requests
import json

# 注册一个新用户
print("1. 注册新用户")
register_url = "http://localhost:8000/api/auth/register"
register_data = {
    "username": "new_test_user2",
    "email": "new_test2@example.com",
    "full_name": "New Test User",
    "password": "new_test_password"
}
register_response = requests.post(register_url, json=register_data)
print(f"注册状态码: {register_response.status_code}")
print(f"注册响应: {register_response.text}")

# 如果注册成功，测试登录
if register_response.status_code == 200:
    print("\n2. 测试用户登录")
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "username": "new_test_user2",
        "password": "new_test_password"
    }
    login_response = requests.post(login_url, json=login_data)
    print(f"登录状态码: {login_response.status_code}")
    print(f"登录响应: {login_response.text}")
    
    # 如果登录成功，测试创建会话
    if login_response.status_code == 200:
        login_data = login_response.json()
        access_token = login_data.get("access_token")
        if access_token:
            print("\n3. 测试创建会话")
            create_session_url = "http://localhost:8000/api/sessions"
            create_session_data = {"title": "测试会话"}
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            create_session_response = requests.post(create_session_url, json=create_session_data, headers=headers)
            print(f"创建会话状态码: {create_session_response.status_code}")
            print(f"创建会话响应: {create_session_response.text}")
            
            # 如果创建会话成功，测试获取会话列表
            if create_session_response.status_code == 200:
                print("\n4. 测试获取会话列表")
                get_sessions_url = "http://localhost:8000/api/sessions"
                get_sessions_response = requests.get(get_sessions_url, headers=headers)
                print(f"获取会话列表状态码: {get_sessions_response.status_code}")
                print(f"获取会话列表响应: {get_sessions_response.text}")
                
                # 解析会话ID，测试获取用户的所有会话
                if get_sessions_response.status_code == 200:
                    sessions_data = get_sessions_response.json()
                    if sessions_data.get("data") and len(sessions_data["data"]) > 0:
                        session = sessions_data["data"][0]
                        user_id = session.get("user_id")
                        if user_id:
                            print("\n5. 测试获取用户的所有会话")
                            get_user_sessions_url = f"http://localhost:8000/api/sessions/users/{user_id}"
                            get_user_sessions_response = requests.get(get_user_sessions_url, headers=headers)
                            print(f"获取用户会话状态码: {get_user_sessions_response.status_code}")
                            print(f"获取用户会话响应: {get_user_sessions_response.text}")