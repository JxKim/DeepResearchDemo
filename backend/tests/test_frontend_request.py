import requests
import json

# 模拟前端请求，测试前后端连接

# API基础URL，与前端配置一致
API_BASE_URL = 'http://localhost:8000/api'

print("=== 测试前端请求 ===")

# 1. 测试简单的GET请求
print("\n1. 测试简单的GET请求...")
try:
    response = requests.get(f"{API_BASE_URL}/auth/users")
    print(f"请求URL: {API_BASE_URL}/auth/users")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print("✅ GET请求成功")
except Exception as e:
    print(f"❌ GET请求失败: {e}")

# 2. 测试登录请求
print("\n2. 测试登录请求...")
login_data = {
    "username": "testuser_api",
    "password": "password123"
}

try:
    response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
    print(f"请求URL: {API_BASE_URL}/auth/login")
    print(f"请求数据: {json.dumps(login_data)}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print("✅ 登录请求成功")
except Exception as e:
    print(f"❌ 登录请求失败: {e}")

# 3. 测试注册请求
print("\n3. 测试注册请求...")
import uuid
random_suffix = str(uuid.uuid4())[:8]
register_data = {
    "username": f"testuser_{random_suffix}",
    "password": "pass123",
    "email": f"test_{random_suffix}@example.com",
    "full_name": f"测试用户_{random_suffix}"
}

try:
    response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data)
    print(f"请求URL: {API_BASE_URL}/auth/register")
    print(f"请求数据: {json.dumps(register_data)}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print("✅ 注册请求成功")
except Exception as e:
    print(f"❌ 注册请求失败: {e}")

# 4. 测试跨域请求
print("\n4. 测试跨域请求...")
try:
    response = requests.post(
        f"{API_BASE_URL}/auth/login", 
        json=login_data,
        headers={
            "Origin": "http://localhost:5173",  # 模拟前端域名
            "Content-Type": "application/json"
        }
    )
    print(f"请求URL: {API_BASE_URL}/auth/login")
    print(f"请求头: Origin: http://localhost:5173")
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
    print("✅ 跨域请求成功")
except Exception as e:
    print(f"❌ 跨域请求失败: {e}")

print("\n=== 测试完成 ===")
