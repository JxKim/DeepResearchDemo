"""
异步飞书服务
基于httpx的异步飞书API调用
"""

import httpx
from typing import Dict, Any, List, Tuple, Optional

from config.loader import get_config
from config.loguru_config import get_logger
from services.http_client import AsyncHTTPClient

logger = get_logger(__name__)
class FeishuAsyncService:
    """异步飞书服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.feishu_config = self.config.feishu
        # 创建带基础URL的客户端
        self.client = AsyncHTTPClient(base_url=self.feishu_config.base_url)
        self._tenant_access_token: Optional[str] = None
    
    async def get_tenant_access_token(self) -> str:
        """异步获取租户访问令牌"""
        if self._tenant_access_token:
            return self._tenant_access_token
            
        url = "/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "app_id": self.feishu_config.app_id,
            "app_secret": self.feishu_config.app_secret
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            
            if response_data.get("code") == 0:
                self._tenant_access_token = response_data.get("tenant_access_token")
                logger.info("飞书租户访问令牌获取成功")
                return self._tenant_access_token
            else:
                raise Exception(f"获取访问令牌失败: {response_data}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"获取飞书token HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"获取飞书token失败: {e}")
            raise
    
    async def create_document(self, title: str) -> str:
        """异步创建飞书文档"""
        token = await self.get_tenant_access_token()
        url = "/open-apis/docx/v1/documents"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
        
        request_body = {
            "title": title
        }
        
        try:
            import requests
            response = await self.client.post(url, headers=headers, json=request_body)
            response.raise_for_status()
            response_json = response.json()
            
            document_id = response_json['data']['document']['document_id']
            logger.info(f"飞书文档创建成功: {document_id}")
            return document_id
            
        except httpx.HTTPStatusError as e:
            logger.error(f"创建飞书文档HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"创建飞书文档失败: {e}")
            raise
    
    async def convert_markdown_to_blocks(self, markdown_content: str) -> Tuple[List[str], List[Dict]]:
        """异步将markdown转换为飞书文档块"""
        token = await self.get_tenant_access_token()
        url = "/open-apis/docx/v1/documents/blocks/convert?user_id_type=user_id"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
        
        request_body = {
            "content_type": "markdown",
            "content": markdown_content
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=request_body)
            response.raise_for_status()
            response_data = response.json()
            
            first_level_block_ids = response_data['data']['first_level_block_ids']
            blocks = response_data['data']['blocks']
            
            logger.info(f"Markdown转换成功，生成 {len(blocks)} 个块")
            return first_level_block_ids, blocks
            
        except httpx.HTTPStatusError as e:
            logger.error(f"转换Markdown HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"转换Markdown失败: {e}")
            raise
    
    async def write_blocks_to_document(self, document_id: str, first_level_block_ids: List[str], 
                                      blocks: List[Dict]) -> Dict:
        """异步将块写入飞书文档"""
        token = await self.get_tenant_access_token()
        url = f"/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/descendant?document_revision_id=-1"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
        
        request_body = {
            "index": 0,
            "children_id": first_level_block_ids,
            "descendants": blocks
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=request_body)
            response.raise_for_status()
            response_data = response.json()
            
            logger.info(f"块写入飞书文档成功: {document_id}")
            return response_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"写入飞书文档HTTP错误: {e}")
            raise
        except Exception as e:
            logger.error(f"写入飞书文档失败: {e}")
            raise
    
    async def save_report_to_feishu(self, file_title: str, file_content: str) -> str:
        """异步保存报告到飞书"""
        try:
            # 1. 创建文档
            document_id = await self.create_document(file_title)
            
            # 2. 转换markdown为块
            first_level_block_ids, blocks = await self.convert_markdown_to_blocks(file_content)
            
            # 3. 写入块到文档
            await self.write_blocks_to_document(document_id, first_level_block_ids, blocks)
            
            # 返回文档链接
            doc_url = f"https://ai.feishu.cn/docx/{document_id}"
            logger.info(f"报告保存成功: {doc_url}")
            return f"写入成功,飞书连接为：{doc_url}"
            
        except Exception as e:
            logger.error(f"保存报告到飞书失败: {e}")
            raise


# 全局飞书服务实例
_feishu_service: Optional[FeishuAsyncService] = None


def get_feishu_service() -> FeishuAsyncService:
    """获取飞书服务实例"""
    global _feishu_service
    if _feishu_service is None:
        _feishu_service = FeishuAsyncService()
    return _feishu_service