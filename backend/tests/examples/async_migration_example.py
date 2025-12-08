"""
异步HTTP客户端迁移示例
演示如何从requests迁移到httpx
"""

import asyncio
import httpx
from loguru import logger

# 导入我们的异步HTTP客户端
from services.http_client import AsyncHTTPClient, get_http_client, http_client_context
from config.loader import get_config


class MigrationExample:
    """迁移示例类"""
    
    def __init__(self):
        self.config = get_config()
    
    # ========== 同步版本（requests） ==========
    
    def sync_get_example(self):
        """同步GET请求示例"""
        # 旧代码（requests）
        import requests
        
        # 直接使用requests（不推荐）
        response = requests.get("https://httpbin.org/get", timeout=30)
        return response.json()
    
    def sync_post_example(self):
        """同步POST请求示例"""
        import requests
        
        data = {"key": "value"}
        response = requests.post("https://httpbin.org/post", json=data, timeout=30)
        return response.json()
    
    # ========== 异步版本（httpx） ==========
    
    async def async_get_example_basic(self):
        """异步GET请求 - 基础版本"""
        # 直接使用httpx.AsyncClient（不推荐用于生产）
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/get")
            return response.json()
    
    async def async_get_example_managed(self):
        """异步GET请求 - 使用管理的客户端"""
        # 使用全局管理的客户端（推荐）
        async with http_client_context() as client:
            response = await client.get("https://httpbin.org/get")
            return response.json()
    
    async def async_post_example_managed(self):
        """异步POST请求 - 使用管理的客户端"""
        data = {"key": "value"}
        
        async with http_client_context() as client:
            response = await client.post("https://httpbin.org/post", json=data)
            return response.json()
    
    async def async_with_retry_example(self):
        """带重试机制的异步请求"""
        from tenacity import retry, stop_after_attempt, wait_exponential
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        async def make_request():
            async with http_client_context() as client:
                response = await client.get("https://httpbin.org/status/500")
                response.raise_for_status()
                return response.json()
        
        try:
            return await make_request()
        except httpx.HTTPStatusError as e:
            logger.error(f"请求失败: {e}")
            return {"error": str(e)}
    
    async def async_batch_requests(self):
        """批量异步请求示例"""
        urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/ip",
            "https://httpbin.org/uuid"
        ]
        
        async with http_client_context() as client:
            # 创建任务列表
            tasks = [client.get(url) for url in urls]
            
            # 并发执行所有请求
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    results.append({"url": urls[i], "error": str(response)})
                else:
                    results.append({"url": urls[i], "data": response.json()})
            
            return results
    
    async def async_with_custom_client(self):
        """使用自定义配置的客户端"""
        # 创建带基础URL的客户端
        client = AsyncHTTPClient(base_url="https://httpbin.org")
        
        # 使用相对路径
        response = await client.get("/get")
        return response.json()


class FeishuServiceAsync:
    """飞书服务异步版本"""
    
    def __init__(self):
        self.config = get_config()
        self.feishu_config = self.config.feishu_config
        # 创建带基础URL的客户端
        self.client = AsyncHTTPClient(base_url=self.feishu_config.base_url)
    
    async def get_tenant_access_token(self):
        """异步获取租户访问令牌"""
        url = "/open-apis/auth/v3/tenant_access_token"
        data = {
            "app_id": self.feishu_config.app_id,
            "app_secret": self.feishu_config.app_secret
        }
        
        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"获取飞书token失败: {e}")
            raise
    
    async def send_message_async(self, receive_id: str, content: dict):
        """异步发送消息"""
        # 先获取token
        token_data = await self.get_tenant_access_token()
        token = token_data["tenant_access_token"]
        
        url = "/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {"receive_id_type": "open_id"}
        data = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": "text"
        }
        
        try:
            response = await self.client.post(url, params=params, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"发送消息失败: {e}")
            raise


async def main():
    """主函数演示"""
    example = MigrationExample()
    feishu_service = FeishuServiceAsync()
    
    logger.info("=== 异步HTTP客户端迁移示例 ===")
    
    # 基础异步请求
    logger.info("1. 基础异步GET请求")
    result1 = await example.async_get_example_managed()
    logger.info(f"结果: {result1}")
    
    # 异步POST请求
    logger.info("2. 异步POST请求")
    result2 = await example.async_post_example_managed()
    logger.info(f"结果: {result2}")
    
    # 批量请求
    logger.info("3. 批量异步请求")
    result3 = await example.async_batch_requests()
    for res in result3:
        logger.info(f"批量结果: {res}")
    
    # 自定义客户端
    logger.info("4. 自定义客户端示例")
    result4 = await example.async_with_custom_client()
    logger.info(f"结果: {result4}")
    
    # 飞书服务示例（需要配置正确的app_id和app_secret）
    logger.info("5. 飞书服务异步示例")
    try:
        # 这里只是演示，实际使用时需要配置正确的飞书应用信息
        # token_result = await feishu_service.get_tenant_access_token()
        # logger.info(f"飞书token: {token_result}")
        logger.info("飞书服务配置检查完成")
    except Exception as e:
        logger.warning(f"飞书服务测试跳过: {e}")
    
    logger.info("=== 示例完成 ===")


if __name__ == "__main__":
    asyncio.run(main())