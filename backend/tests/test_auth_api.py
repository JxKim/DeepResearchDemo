import requests
import json

# API基础URL
API_BASE_URL = 'http://localhost:8000/api'

# 测试用户名和密码
test_username = 'testuser_api'
test_password = 'password123'
test_email = 'test_api@example.com'
test_full_name = '测试用户API'

print("=== 测试用户认证API ===")

# 1. 测试用户注册
print("\n1. 测试用户注册...")
register_data = {
    "username": test_username,
    "password": test_password,
    "email": test_email,
    "full_name": test_full_name
}

register_response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data)
print(f"注册响应状态码: {register_response.status_code}")
print(f"注册响应内容: {register_response.text}")

if register_response.status_code == 200:
    # 提取访问令牌
    register_result = register_response.json()
    access_token = register_result.get('access_token')
    print(f"✅ 注册成功！访问令牌: {access_token}")
else:
    print("❌ 注册失败")
    exit(1)

# 2. 测试用户登录
print("\n2. 测试用户登录...")
login_data = {
    "username": test_username,
    "password": test_password
}

login_response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
print(f"登录响应状态码: {login_response.status_code}")
print(f"登录响应内容: {login_response.text}")

if login_response.status_code == 200:
    # 提取访问令牌
    login_result = login_response.json()
    access_token = login_result.get('access_token')
    print(f"✅ 登录成功！访问令牌: {access_token}")
else:
    print("❌ 登录失败")
    exit(1)

# 3. 测试验证令牌
print("\n3. 测试验证令牌...")
verify_response = requests.post(f"{API_BASE_URL}/auth/verify?token={access_token}")
print(f"验证响应状态码: {verify_response.status_code}")
print(f"验证响应内容: {verify_response.text}")

if verify_response.status_code == 200:
    verify_result = verify_response.json()
    if verify_result.get('success'):
        print(f"✅ 令牌验证成功！用户: {verify_result['data']['username']}")
    else:
        print("❌ 令牌验证失败")
        exit(1)
else:
    print("❌ 令牌验证失败")
    exit(1)

# 4. 测试获取当前用户信息
print("\n4. 测试获取当前用户信息...")
me_response = requests.get(f"{API_BASE_URL}/auth/me?token={access_token}")
print(f"获取用户信息响应状态码: {me_response.status_code}")
print(f"获取用户信息响应内容: {me_response.text}")

if me_response.status_code == 200:
    me_result = me_response.json()
    print(f"✅ 获取用户信息成功！用户: {me_result['username']}, 邮箱: {me_result['email']}")
else:
    print("❌ 获取用户信息失败")
    exit(1)

# 5. 测试用户登出
print("\n5. 测试用户登出...")
logout_response = requests.post(f"{API_BASE_URL}/auth/logout?token={access_token}")
print(f"登出响应状态码: {logout_response.status_code}")
print(f"登出响应内容: {logout_response.text}")

if logout_response.status_code == 200:
    logout_result = logout_response.json()
    if logout_result.get('success'):
        print(f"✅ 登出成功！消息: {logout_result['message']}")
    else:
        print("❌ 登出失败")
        exit(1)
else:
    print("❌ 登出失败")
    exit(1)

# 6. 测试验证已登出的令牌
print("\n6. 测试验证已登出的令牌...")
verify_logout_response = requests.post(f"{API_BASE_URL}/auth/verify?token={access_token}")
print(f"验证已登出令牌响应状态码: {verify_logout_response.status_code}")
print(f"验证已登出令牌响应内容: {verify_logout_response.text}")

if verify_logout_response.status_code == 200:
    verify_logout_result = verify_logout_response.json()
    if not verify_logout_result.get('success'):
        print(f"✅ 验证已登出的令牌成功！令牌已失效")
    else:
        print("❌ 验证已登出的令牌失败: 令牌仍有效")
        exit(1)
else:
    print("❌ 验证已登出的令牌失败")
    exit(1)

print("\n=== 所有测试通过！用户认证API工作正常 ===")
