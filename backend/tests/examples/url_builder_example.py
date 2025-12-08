"""
URL构建最佳实践示例
展示不同URL构建方式的优缺点
"""

from config.loader import get_config
from config.loguru_config import get_logger
from urllib.parse import urljoin
from typing import Dict, Optional

logger = get_logger("url_builder")

class URLBuilder:
    """URL构建器 - 最佳实践实现"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')  # 移除末尾斜杠
        
    def build_url(self, endpoint: str) -> str:
        """安全构建完整URL"""
        # 确保endpoint以斜杠开头
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        # 使用urljoin确保路径正确拼接
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def build_url_with_params(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """构建带查询参数的URL"""
        from urllib.parse import urlencode
        
        url = self.build_url(endpoint)
        
        if params:
            # 过滤掉None值
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                url += '?' + urlencode(filtered_params)
                
        return url
    
    def build_template_url(self, endpoint: str, **kwargs) -> str:
        """构建模板URL（支持路径参数）"""
        url = self.build_url(endpoint)
        
        # 替换路径参数
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))
                
        return url


def demonstrate_direct_concatenation():
    """演示直接字符串拼接的问题"""
    logger.info("=== 直接字符串拼接的问题 ===")
    
    base_url = "https://open.feishu.cn"
    endpoints = {
        "get_tenant_token": "/open-apis/auth/v3/tenant_access_token/internal",
        "send_message": "open-apis/im/v1/messages",  # 缺少开头的斜杠
        "upload_file": "/open-apis/drive/v1/files/upload_all/"  # 末尾有斜杠
    }
    
    # 问题1：路径拼接错误
    for name, endpoint in endpoints.items():
        # 直接拼接
        direct_url = base_url + endpoint
        logger.warning(f"直接拼接 {name}: {direct_url}")
        
        # 正确方式
        builder = URLBuilder(base_url)
        correct_url = builder.build_url(endpoint)
        logger.info(f"正确构建 {name}: {correct_url}")
    
    # 问题2：参数处理
    params = {"user_id": "123", "page_size": 20, "cursor": None}
    endpoint = "/open-apis/contact/v3/users"
    
    # 错误方式：手动拼接参数
    param_strs = []
    for k, v in params.items():
        if v is not None:
            param_strs.append(f"{k}={v}")
    wrong_url = base_url + endpoint + "?" + "&".join(param_strs)
    logger.warning(f"手动参数拼接: {wrong_url}")
    
    # 正确方式
    correct_url = URLBuilder(base_url).build_url_with_params(endpoint, params)
    logger.info(f"正确参数构建: {correct_url}")


def demonstrate_urljoin_advantages():
    """演示urljoin的优势"""
    logger.info("=== urljoin的优势 ===")
    
    base_url = "https://open.feishu.cn"
    test_cases = [
        ("/api/v1/users", "标准路径"),
        ("api/v1/users", "缺少开头的斜杠"),
        ("/api/v1/users/", "末尾有斜杠"),
        ("./api/v1/users", "相对路径"),
        ("./../api/v1/users", "相对路径包含上级目录"),
    ]
    
    for endpoint, description in test_cases:
        # 直接拼接
        direct_result = base_url + endpoint
        
        # 使用urljoin
        builder = URLBuilder(base_url)
        urljoin_result = builder.build_url(endpoint)
        
        logger.info(f"\n{description}:")
        logger.info(f"  直接拼接: {direct_result}")
        logger.info(f"  urljoin: {urljoin_result}")
        
        if direct_result != urljoin_result:
            logger.warning("  ⚠️ 结果不同！")


def demonstrate_template_urls():
    """演示模板URL构建"""
    logger.info("=== 模板URL构建 ===")
    
    base_url = "https://open.feishu.cn"
    builder = URLBuilder(base_url)
    
    # 模板端点
    template_endpoints = {
        "get_user_info": "/open-apis/contact/v3/users/{user_id}",
        "update_message": "/open-apis/im/v1/messages/{message_id}",
        "get_file_info": "/open-apis/drive/v1/files/{file_token}"
    }
    
    for name, template in template_endpoints.items():
        # 构建具体URL
        if name == "get_user_info":
            url = builder.build_template_url(template, user_id="u123456")
        elif name == "update_message":
            url = builder.build_template_url(template, message_id="om_abc123")
        else:
            url = builder.build_template_url(template, file_token="boxcnabc123")
            
        logger.info(f"{name}: {url}")


def demonstrate_feishu_url_builder():
    """演示飞书URL构建器"""
    logger.info("=== 飞书URL构建器 ===")
    
    config = get_config()
    feishu_config = config.feishu
    
    # 创建飞书专用的URL构建器
    feishu_builder = URLBuilder(feishu_config.base_url)
    
    # 构建各种API URL
    endpoints = feishu_config.endpoints
    
    logger.info("飞书API URL构建:")
    for api_name, endpoint in endpoints.items():
        url = feishu_builder.build_url(endpoint)
        logger.info(f"  {api_name}: {url}")
    
    # 演示带参数的URL
    params = {"user_id_type": "open_id", "department_id_type": "open_department_id"}
    users_url = feishu_builder.build_url_with_params(
        "/open-apis/contact/v3/users", 
        params
    )
    logger.info(f"带参数的用户列表URL: {users_url}")
    
    # 演示模板URL
    message_url = feishu_builder.build_template_url(
        "/open-apis/im/v1/messages/{message_id}",
        message_id="om_abc123"
    )
    logger.info(f"模板消息URL: {message_url}")


def main():
    """主演示函数"""
    logger.info("开始演示URL构建最佳实践")
    
    try:
        demonstrate_direct_concatenation()
        demonstrate_urljoin_advantages()
        demonstrate_template_urls()
        demonstrate_feishu_url_builder()
        
        logger.info("URL构建演示完成")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()