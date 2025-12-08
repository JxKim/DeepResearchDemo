"""
配置系统使用示例
展示如何在不同模块中使用统一的配置系统
"""
import os
import sys
sys.path.insert(0, r'D:\PycharmProjects\projects\SmartAgent\backend')
from config.loader import get_config
from config.loguru_config import get_logger

# 获取配置和日志器
config = get_config()
logger = get_logger("config_example")

def demonstrate_feishu_config():
    """演示飞书配置使用"""
    logger.info("=== 飞书配置演示 ===")
    
    feishu_config = config.feishu
    
    logger.info(f"飞书应用ID: {feishu_config.app_id}")
    logger.info(f"飞书API基础URL: {feishu_config.base_url}")
    logger.info(f"请求超时时间: {feishu_config.timeout}秒")
    
    # 演示API端点使用
    endpoints = feishu_config.endpoints
    logger.info("飞书API端点:")
    for name, endpoint in endpoints.items():
        logger.info(f"  {name}: {endpoint}")
    
    # 模拟API调用
    def build_feishu_url(endpoint_name: str) -> str:
        endpoint = endpoints.get(endpoint_name)
        if endpoint:
            return f"{feishu_config.base_url}{endpoint}"
        raise ValueError(f"未知的端点: {endpoint_name}")
    
    try:
        token_url = build_feishu_url("get_tenant_token")
        logger.info(f"获取租户令牌URL: {token_url}")
    except ValueError as e:
        logger.error(f"构建URL失败: {e}")

def demonstrate_llm_config():
    """演示LLM配置使用"""
    logger.info("=== LLM配置演示 ===")
    
    llm_config = config.llm
    
    logger.info(f"LLM提供商: {llm_config.provider}")
    logger.info(f"使用模型: {llm_config.model}")
    logger.info(f"温度参数: {llm_config.temperature}")
    logger.info(f"最大令牌数: {llm_config.max_tokens}")
    
    # 模拟API调用配置
    def build_llm_request_config():
        return {
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "model": llm_config.model,
            "temperature": llm_config.temperature,
            "max_tokens": llm_config.max_tokens,
            "timeout": llm_config.timeout
        }
    
    request_config = build_llm_request_config()
    logger.info("LLM请求配置:")
    for key, value in request_config.items():
        if key == "api_key":
            logger.info(f"  {key}: {'*' * 8}{value[-4:]}")  # 隐藏敏感信息
        else:
            logger.info(f"  {key}: {value}")

def demonstrate_database_config():
    """演示数据库配置使用"""
    logger.info("=== 数据库配置演示 ===")
    
    db_config = config.database
    
    logger.info(f"数据库URL: {db_config.url}")
    logger.info(f"SQL回显: {db_config.echo}")
    logger.info(f"连接池大小: {db_config.pool_size}")
    logger.info(f"最大溢出连接: {db_config.max_overflow}")

def demonstrate_security_config():
    """演示安全配置使用"""
    logger.info("=== 安全配置演示 ===")
    
    security_config = config.security
    
    logger.info(f"JWT算法: {security_config.algorithm}")
    logger.info(f"访问令牌过期时间: {security_config.access_token_expire_minutes}分钟")
    logger.info(f"CORS允许的源: {security_config.cors_origins}")

def demonstrate_environment_config():
    """演示环境配置使用"""
    logger.info("=== 环境配置演示 ===")
    
    logger.info(f"当前环境: {config.environment}")
    logger.info(f"调试模式: {config.debug}")
    
    # 根据环境执行不同逻辑
    if config.environment.value == "development":
        logger.info("当前为开发环境，启用详细日志和热重载")
    elif config.environment.value == "production":
        logger.info("当前为生产环境，启用性能优化和安全设置")

def main():
    """主演示函数"""
    logger.info("开始演示配置系统使用")
    
    try:
        demonstrate_environment_config()
        demonstrate_feishu_config()
        demonstrate_llm_config()
        demonstrate_database_config()
        demonstrate_security_config()
        
        logger.info("配置系统演示完成")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()