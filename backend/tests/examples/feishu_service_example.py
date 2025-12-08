"""
飞书服务URL构建最佳实践示例
"""

from config.loader import get_config
from config.loguru_config import get_logger

logger = get_logger("feishu_service")

class FeishuService:
    """飞书服务类 - 使用最佳实践的URL构建"""
    
    def __init__(self):
        self.config = get_config()
        self.feishu_config = self.config.feishu
        self.builder = self.feishu_config.url_builder
    
    def get_tenant_token_url(self) -> str:
        """获取租户令牌URL"""
        endpoint = self.feishu_config.endpoints["get_tenant_token"]
        return self.builder.build_url(endpoint)
    
    def send_message_url(self, receive_id_type: str = "open_id") -> str:
        """发送消息URL（带参数）"""
        endpoint = self.feishu_config.endpoints["send_message"]
        params = {"receive_id_type": receive_id_type}
        return self.builder.build_url_with_params(endpoint, params)
    
    def get_user_info_url(self, user_id: str) -> str:
        """获取用户信息URL（模板参数）"""
        endpoint = self.feishu_config.endpoints["get_user_info"]
        return self.builder.build_template_url(endpoint, user_id=user_id)
    
    def upload_file_url(self) -> str:
        """上传文件URL"""
        endpoint = self.feishu_config.endpoints["upload_file"]
        return self.builder.build_url(endpoint)
    
    def demonstrate_all_urls(self):
        """演示所有URL构建"""
        logger.info("=== 飞书API URL构建演示 ===")
        
        # 基础URL
        logger.info(f"飞书基础URL: {self.feishu_config.base_url}")
        
        # 各种URL构建
        urls = {
            "租户令牌": self.get_tenant_token_url(),
            "发送消息": self.send_message_url(),
            "用户信息": self.get_user_info_url("u123456"),
            "上传文件": self.upload_file_url(),
        }
        
        for name, url in urls.items():
            logger.info(f"{name} URL: {url}")
        
        # 演示参数变化
        logger.info("\n=== 参数变化演示 ===")
        
        # 不同的接收ID类型
        for receive_id_type in ["open_id", "user_id", "union_id"]:
            url = self.send_message_url(receive_id_type)
            logger.info(f"发送消息 ({receive_id_type}): {url}")
        
        # 不同的用户ID
        for user_id in ["u123456", "u789012", "admin_user"]:
            url = self.get_user_info_url(user_id)
            logger.info(f"用户信息 ({user_id}): {url}")


def demonstrate_error_cases():
    """演示错误情况处理"""
    logger.info("\n=== 错误情况处理演示 ===")
    
    config = get_config()
    feishu_config = config.feishu
    builder = feishu_config.url_builder
    
    # 测试各种endpoint格式
    test_endpoints = [
        "/api/v1/test",           # 标准格式
        "api/v1/test",            # 缺少开头的斜杠
        "/api/v1/test/",          # 末尾有斜杠
        "./api/v1/test",          # 相对路径
        "../api/v1/test",         # 上级目录
    ]
    
    for endpoint in test_endpoints:
        try:
            url = builder.build_url(endpoint)
            logger.info(f"endpoint: '{endpoint}' -> URL: {url}")
        except Exception as e:
            logger.error(f"endpoint: '{endpoint}' 构建失败: {e}")


def main():
    """主演示函数"""
    logger.info("开始飞书服务URL构建演示")
    
    try:
        # 创建飞书服务实例
        feishu_service = FeishuService()
        
        # 演示URL构建
        feishu_service.demonstrate_all_urls()
        
        # 演示错误处理
        demonstrate_error_cases()
        
        logger.info("飞书服务URL构建演示完成")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()