import requests

# API基础URL
API_BASE_URL = 'http://localhost:8000/api'

# 测试用户名和密码
invalid_username = 'invaliduser'
invalid_password = 'invalidpass'
valid_username = 'testuser_api'
valid_password = 'password123'

print("=== 测试登录错误处理 ===")

# 1. 测试无效用户名
print("\n1. 测试无效用户名...")
login_data = {
    "username": invalid_username,
    "password": valid_password
}

login_response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
print(f"登录响应状态码: {login_response.status_code}")
print(f"登录响应内容: {login_response.text}")

if login_response.status_code == 401:
    print("✅ 无效用户名处理正确，返回401状态码")
else:
    print("❌ 无效用户名处理错误，返回了错误的状态码")

# 2. 测试无效密码
print("\n2. 测试无效密码...")
login_data = {
    "username": valid_username,
    "password": invalid_password
}

login_response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
print(f"登录响应状态码: {login_response.status_code}")
print(f"登录响应内容: {login_response.text}")

if login_response.status_code == 401:
    print("✅ 无效密码处理正确，返回401状态码")
else:
    print("❌ 无效密码处理错误，返回了错误的状态码")

# 3. 测试有效用户名和密码
print("\n3. 测试有效用户名和密码...")
login_data = {
    "username": valid_username,
    "password": valid_password
}

login_response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
print(f"登录响应状态码: {login_response.status_code}")
print(f"登录响应内容: {login_response.text}")

if login_response.status_code == 200:
    print("✅ 有效用户名和密码处理正确，返回200状态码")
else:
    print("❌ 有效用户名和密码处理错误，返回了错误的状态码")

print("\n=== 测试完成 ===")
