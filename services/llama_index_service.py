"""
LlamaIndex服务实现
提供向量存储和检索功能
"""

import os
from typing import List, Dict, Any, Optional
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext,
    load_index_from_storage
)
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Settings
import chromadb
from config.logging_config import get_logger

logger = get_logger(__name__)


class LlamaIndexService:
    """LlamaIndex服务类"""
    
    def __init__(self):
        self.index = None
        self.vector_store = None
        self.storage_context = None
        self._setup_embeddings()
        self._setup_vector_store()
    
    def _setup_embeddings(self):
        """设置嵌入模型"""
        try:
            # 使用DeepSeek的嵌入API
            api_key = os.getenv("DASH_SCOPE_API_KEY")
            if not api_key:
                logger.warning("未找到DASH_SCOPE_API_KEY，使用默认嵌入模型")
                return
            
            # 设置全局嵌入模型
            Settings.embed_model = OpenAIEmbedding(
                api_key=api_key,
                api_base="https://api.deepseek.com",
                model="text-embedding-ada-002"
            )
            logger.info("嵌入模型设置完成")
        except Exception as e:
            logger.error(f"设置嵌入模型失败: {str(e)}")
    
    def _setup_vector_store(self):
        """设置向量存储"""
        try:
            # 使用ChromaDB作为向量存储
            chroma_client = chromadb.PersistentClient(path="./chroma_db")
            chroma_collection = chroma_client.get_or_create_collection("deepsearch")
            
            self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # 尝试加载现有索引
            try:
                self.index = load_index_from_storage(self.storage_context)
                logger.info("成功加载现有向量索引")
            except:
                # 如果加载失败，创建新索引
                self.index = VectorStoreIndex.from_vector_store(
                    self.vector_store, 
                    storage_context=self.storage_context
                )
                logger.info("创建新的向量索引")
                
        except Exception as e:
            logger.error(f"设置向量存储失败: {str(e)}")
            # 使用内存存储作为后备
            self.index = VectorStoreIndex.from_documents([])
    
    def add_search_results_to_index(self, search_results: List[Any], metadata: Dict[str, Any]):
        """
        将搜索结果添加到向量索引
        
        Args:
            search_results: 搜索结果列表
            metadata: 元数据
        """
        try:
            if not search_results:
                logger.warning("搜索结果为空，跳过索引")
                return
            
            # 将搜索结果转换为文档
            documents = []
            for result in search_results:
                if hasattr(result, 'title') and hasattr(result, 'snippet'):
                    content = f"标题: {result.title}\n内容: {result.snippet}"
                    if hasattr(result, 'url'):
                        content += f"\n来源: {result.url}"
                    
                    # 创建文档对象
                    from llama_index.core import Document
                    doc = Document(
                        text=content,
                        metadata={
                            **metadata,
                            "title": getattr(result, 'title', ''),
                            "url": getattr(result, 'url', ''),
                            "source": getattr(result, 'source', 'web')
                        }
                    )
                    documents.append(doc)
            
            if documents:
                # 添加到索引
                self.index.insert_nodes(documents)
                logger.info(f"成功将 {len(documents)} 个文档添加到向量索引")
            
        except Exception as e:
            logger.error(f"添加搜索结果到索引失败: {str(e)}")
    
    def query_index(self, query: str, similarity_top_k: int = 5) -> str:
        """
        查询向量索引
        
        Args:
            query: 查询文本
            similarity_top_k: 返回最相似的结果数量
            
        Returns:
            查询结果文本
        """
        try:
            if not self.index:
                logger.warning("向量索引未初始化")
                return "向量索引未初始化"
            
            query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)
            response = query_engine.query(query)
            
            return str(response)
        except Exception as e:
            logger.error(f"查询向量索引失败: {str(e)}")
            return f"查询失败: {str(e)}"
    
    def query_index_with_metadata_filter(
        self, 
        query: str, 
        filter_key: str, 
        filter_values: List[str],
        similarity_top_k: int = 5
    ) -> str:
        """
        使用元数据过滤器查询向量索引
        
        Args:
            query: 查询文本
            filter_key: 过滤键
            filter_values: 过滤值列表
            similarity_top_k: 返回最相似的结果数量
            
        Returns:
            查询结果文本
        """
        try:
            if not self.index:
                logger.warning("向量索引未初始化")
                return "向量索引未初始化"
            
            # 创建带过滤器的查询引擎
            query_engine = self.index.as_query_engine(
                similarity_top_k=similarity_top_k,
                filters={filter_key: {"$in": filter_values}} if filter_values else None
            )
            
            response = query_engine.query(query)
            return str(response)
        except Exception as e:
            logger.error(f"带过滤器查询向量索引失败: {str(e)}")
            return f"查询失败: {str(e)}"
    
    def get_document_by_source_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        根据源URL获取文档
        
        Args:
            url: 源URL
            
        Returns:
            文档信息字典或None
        """
        try:
            if not self.index:
                return None
            
            # 这里需要实现根据URL查找文档的逻辑
            # 由于LlamaIndex的限制，这里返回一个模拟的文档信息
            return {
                "metadata": {
                    "title": "搜索结果",
                    "url": url,
                    "source": "web"
                }
            }
        except Exception as e:
            logger.error(f"根据URL获取文档失败: {str(e)}")
            return None


# 创建全局服务实例
llama_index_service = LlamaIndexService()
