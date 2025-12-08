from controllers.auth_controller import (
    register_user, login_user, verify_token, get_user_by_id,
    update_user, delete_user, get_all_users, logout_user,
    get_user_profile, update_user_profile
)
from tests.models import UserCreate, LoginRequest, UserUpdate

# 测试用户数据
import uuid
random_suffix = str(uuid.uuid4())[:8]
test_user_data = UserCreate(
    username=f"testuser_{random_suffix}",
    email=f"test_{random_suffix}@example.com",
    full_name="测试用户",
    password="pass123"
)

updated_user_data = UserUpdate(
    email=f"updated_{random_suffix}@example.com",
    full_name="更新后的测试用户",
    password="newpass456"
)

print("=== 开始测试用户认证和登录模块 ===")

# 1. 测试用户注册
print("\n1. 测试用户注册...")
try:
    token_response = register_user(test_user_data)
    print(f"✅ 注册成功！访问令牌: {token_response.access_token}")
    access_token = token_response.access_token
except Exception as e:
    print(f"❌ 注册失败: {e}")
    exit(1)

# 2. 测试用户登录
print("\n2. 测试用户登录...")
try:
    login_request = LoginRequest(
        username=test_user_data.username,
        password=test_user_data.password
    )
    login_response = login_user(login_request)
    print(f"✅ 登录成功！访问令牌: {login_response.access_token}")
    login_token = login_response.access_token
except Exception as e:
    print(f"❌ 登录失败: {e}")
    exit(1)

# 3. 测试验证令牌
print("\n3. 测试验证令牌...")
try:
    user = verify_token(access_token)
    print(f"✅ 令牌验证成功！用户: {user.username}")
    user_id = user.id
except Exception as e:
    print(f"❌ 令牌验证失败: {e}")
    exit(1)

# 4. 测试获取用户信息
print("\n4. 测试获取用户信息...")
try:
    user = get_user_by_id(user_id)
    print(f"✅ 获取用户信息成功！用户: {user.username}, 邮箱: {user.email}")
except Exception as e:
    print(f"❌ 获取用户信息失败: {e}")
    exit(1)

# 5. 测试获取用户资料
print("\n5. 测试获取用户资料...")
try:
    user_profile = get_user_profile(user_id)
    print(f"✅ 获取用户资料成功！用户: {user_profile.username}, 邮箱: {user_profile.email}")
except Exception as e:
    print(f"❌ 获取用户资料失败: {e}")
    exit(1)

# 6. 测试更新用户信息
print("\n6. 测试更新用户信息...")
try:
    updated_user = update_user(user_id, updated_user_data)
    print(f"✅ 更新用户信息成功！新邮箱: {updated_user.email}, 新名称: {updated_user.full_name}")
except Exception as e:
    print(f"❌ 更新用户信息失败: {e}")
    exit(1)

# 7. 测试更新用户资料
print("\n7. 测试更新用户资料...")
try:
    updated_profile = update_user_profile(user_id, UserUpdate(full_name="再次更新的测试用户"))
    print(f"✅ 更新用户资料成功！新名称: {updated_profile.full_name}")
except Exception as e:
    print(f"❌ 更新用户资料失败: {e}")
    exit(1)

# 8. 测试获取所有用户
print("\n8. 测试获取所有用户...")
try:
    all_users = get_all_users()
    print(f"✅ 获取所有用户成功！用户数量: {len(all_users.data)}")
    for user in all_users.data:
        print(f"   - {user.username} ({user.email})")
except Exception as e:
    print(f"❌ 获取所有用户失败: {e}")
    exit(1)

# 9. 测试使用新密码登录
print("\n9. 测试使用新密码登录...")
try:
    new_login_request = LoginRequest(
        username=test_user_data.username,
        password="newpass456"
    )
    new_login_response = login_user(new_login_request)
    print(f"✅ 使用新密码登录成功！访问令牌: {new_login_response.access_token}")
    new_access_token = new_login_response.access_token
except Exception as e:
    print(f"❌ 使用新密码登录失败: {e}")
    exit(1)

# 10. 测试用户登出
print("\n10. 测试用户登出...")
try:
    logout_response = logout_user(access_token)
    print(f"✅ 登出成功！消息: {logout_response.message}")
except Exception as e:
    print(f"❌ 登出失败: {e}")
    exit(1)

# 11. 测试验证已登出的令牌
print("\n11. 测试验证已登出的令牌...")
try:
    user = verify_token(access_token)
    if user is None:
        print("✅ 验证已登出的令牌成功！令牌已失效")
    else:
        print("❌ 验证已登出的令牌失败: 令牌仍有效")
        exit(1)
except Exception as e:
    print(f"✅ 验证已登出的令牌成功！令牌已失效: {e}")

# 12. 测试删除用户
print("\n12. 测试删除用户...")
try:
    delete_response = delete_user(user_id)
    print(f"✅ 删除用户成功！消息: {delete_response.message}")
except Exception as e:
    print(f"❌ 删除用户失败: {e}")
    exit(1)

# 13. 测试获取已删除的用户
print("\n13. 测试获取已删除的用户...")
try:
    user = get_user_by_id(user_id)
    if user is None:
        print("✅ 获取已删除的用户成功！用户不存在")
    else:
        print("❌ 获取已删除的用户失败: 用户仍存在")
        exit(1)
except Exception as e:
    print(f"❌ 获取已删除的用户失败: {e}")
    exit(1)

print("\n=== 所有测试通过！用户认证和登录模块工作正常 ===")
