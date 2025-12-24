from services.parsers.base import BaseParser
from typing import List
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from config.loader import get_config
from config.loguru_config import get_logger
from services.http_client import AsyncHTTPClient
from services.parsers.markdown_parser import MarkdownParser
import time
config = get_config()
logger = get_logger(__name__)



class UnstructuredPDFParser(BaseParser):
    """
    PDF文件解析器，只针对非扫描型PDF文件做处理，未对扫描型做任何处理

    todo-list
    1、目录页识别
    2、title-based 合并，
    3、表格识别，将表格单独作为一个元素
    

    """

    def parse(self, file_path: str) -> List:
        """
        解析PDF文件内容，此处
        :param file_path: PDF文件路径
        :return: 解析后的文本内容
        """
        logger.info(f"开始解析PDF文件 {file_path}")
        start_time = time.time()
        # todo 使用UnstructuredPDFLoader解析，现在速度太慢了，怎么优化？
        elements = UnstructuredPDFLoader(
            file_path=file_path,
            mode="elements",
            strategy="hi_res",
            infer_table_structure=True,
            languages=["eng","chi_sim"]
            ).load()
        
        end_time = time.time()
        logger.info(f"成功解析PDF文件 {file_path}，耗时: {end_time - start_time} 秒")
        # elements = partition_pdf(file_path)
        return elements

class MineruPDFLoader(BaseParser):
    """
    使用Mineru解析PDF文件
    本地部署Mineru，解决数据安全性问题
    todo:
    1、怎么评估本地部署的mineru的性能，最大可以支持多少qps?
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        pass
        # self.http_client = AsyncHTTPClient(base_url=config.mineru_config.base_url)

    
    def parse(self, file_path: str,file_name:str) -> List:
        """
        解析PDF文件内容
        :param file_path: PDF文件路径
        :return: 解析后的文本内容
        """
        # 先使用Mineru解析PDF文件，将其解析成markdown文件，然后再使用MarkdownParser解析markdown文件内容
        logger.info("使用Mineru解析PDF文件")

        try:
            import requests
            from pathlib import Path

            mineru_cfg = getattr(config, "mineru", None)
            if mineru_cfg is None:
                raise Exception("Mineru配置缺失")

            base_url = str(mineru_cfg.base_url).rstrip("/")
            parse_endpoint = str(mineru_cfg.parse_endpoint)
            parse_url = f"{base_url}{parse_endpoint}"

            backend = "vlm-vllm-async-engine" if getattr(mineru_cfg, "use_vllm", False) else "pipeline"
            logger.info(f"使用Mineru后端: {backend}")
            request_data = {
                "backend": backend,
                "return_md": "true",
                "start_page_id":0,
                "end_page_id":5
            }

            upload_name = file_name or Path(file_path).name
            with open(file_path, "rb") as f:
                request_files = [("files", (upload_name, f, "application/pdf"))]
                response = requests.post(
                    url=parse_url,
                    data=request_data,
                    files=request_files,
                )

            
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"Mineru解析失败: {response.text}")
                raise Exception(f"Mineru解析失败: {response.text}")

            # 获取解析结果
            result = response.json()
            logger.info(result.keys())
            # 如果 Mineru 返回的是 markdown 内容字符串
            if "results" in result:

                md_content = result["results"][file_name]["md_content"]
                md_content = MarkdownParser._clean_markdown(md_content)
                # 这里可能需要将字符串保存为临时文件再给 MarkdownParser 解析，或者 MarkdownParser 支持直接解析字符串
                # 假设 MarkdownParser 需要文件路径，我们先保存为临时文件
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
                    tmp_md.write(md_content)
                    tmp_md_path = tmp_md.name
                    
                try:
                    logger.info(f"临时文件路径: {tmp_md_path}，开始启动Markdown解析")
                    markdown_parser = MarkdownParser()
                    documents = markdown_parser.parse(tmp_md_path)
                    logger.info(f"Markdown解析完成，共解析出 {len(documents)} 个文档片段")
                    return documents
                finally:
                    if os.path.exists(tmp_md_path):
                        os.remove(tmp_md_path)
            
            # 兼容 Mineru 的其他返回格式
            # 如果返回的是 output_dir 中的文件路径信息
            elif "file" in result:
                 md_file = result["file"]
                 markdown_parser = MarkdownParser()
                 documents = markdown_parser.parse(md_file)
                 return documents
                 
            # 如果返回的是详细的对象结构，包含 content 等字段
            # 注意：实际使用中可能需要根据 Mineru 的实际返回结构调整
            # 比如，如果它返回一个包含多个文件的列表或特定的 JSON 结构
            elif "result" in result and "markdown" in result["result"]:
                 md_content = result["result"]["markdown"]
                 # 处理逻辑同上
                 import tempfile
                 import os
                 with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
                    tmp_md.write(md_content)
                    tmp_md_path = tmp_md.name
                 try:
                    markdown_parser = MarkdownParser()
                    documents = markdown_parser.parse(tmp_md_path)
                    return documents
                 finally:
                    if os.path.exists(tmp_md_path):
                        os.remove(tmp_md_path)

            else:
                logger.warning(f"未知的 Mineru 返回格式: {result.keys()}")
                # 尝试直接解析返回内容（如果它本身就是 markdown 文本）
                # 但通常它是一个 JSON
                return []

        except Exception as e:
            logger.error(f"PDF解析过程出错: {e}")
            raise e

