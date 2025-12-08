"""
Loguru使用示例
展示如何在不同的模块和层中使用loguru
"""

from config.loguru_config import get_logger

# 示例1: 基本使用
logger = get_logger("example_module")

def basic_usage():
    """基本日志使用示例"""
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    
    # 带上下文信息的日志
    logger.info("用户登录成功", user_id=123, username="张三")
    
    # 异常日志
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("计算过程中发生错误")

def structured_logging():
    """结构化日志示例"""
    # 使用bind绑定额外上下文
    api_logger = logger.bind(api_name="user_login", version="v1.0")
    
    api_logger.info("API请求开始", method="POST", endpoint="/api/login")
    
    # 模拟处理过程
    api_logger.debug("验证用户凭证")
    
    # 模拟成功响应
    api_logger.info("API请求完成", status="success", duration="150ms")

def performance_logging():
    """性能日志示例"""
    import time
    
    # 使用decorator记录函数执行时间
    @logger.catch
    def expensive_operation():
        time.sleep(0.1)
        return "操作完成"
    
    # 手动记录执行时间
    start_time = time.time()
    result = expensive_operation()
    end_time = time.time()
    
    logger.info("操作执行完成", 
                operation="expensive_operation", 
                duration=f"{(end_time - start_time)*1000:.2f}ms",
                result=result)

class UserService:
    """用户服务类示例"""
    
    def __init__(self):
        # 每个类使用自己的logger实例
        self.logger = get_logger("UserService")
    
    def create_user(self, username: str, email: str):
        """创建用户"""
        self.logger.info("开始创建用户", username=username, email=email)
        
        # 模拟业务逻辑
        try:
            # 验证用户名
            if len(username) < 3:
                raise ValueError("用户名太短")
            
            # 模拟数据库操作
            self.logger.debug("保存用户到数据库")
            
            # 模拟成功
            user_id = 123
            self.logger.info("用户创建成功", user_id=user_id)
            return user_id
            
        except Exception as e:
            self.logger.error("用户创建失败", error=str(e))
            raise

if __name__ == "__main__":
    print("=== Loguru使用示例 ===")
    
    print("\n1. 基本使用:")
    basic_usage()
    
    print("\n2. 结构化日志:")
    structured_logging()
    
    print("\n3. 性能日志:")
    performance_logging()
    
    print("\n4. 类中使用:")
    user_service = UserService()
    try:
        user_service.create_user("张三", "zhangsan@example.com")
        user_service.create_user("ab", "ab@example.com")  # 这个会失败
    except:
        pass
    
    print("\n示例执行完成，请查看日志文件中的输出")