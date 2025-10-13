"""
搜索工具实现
提供网络搜索功能
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    url: str
    snippet: str
    source: str = "web"


class SearchTool:
    """搜索工具类"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 使用DuckDuckGo作为搜索源
            search_results = await self._duckduckgo_search(query, num_results)
            logger.info(f"搜索 '{query}' 获得 {len(search_results)} 个结果")
            return search_results
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    async def _duckduckgo_search(self, query: str, num_results: int) -> List[SearchResult]:
        """使用DuckDuckGo进行搜索"""
        try:
            # 构建搜索URL
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            session = await self._get_session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_duckduckgo_results(html, num_results)
                else:
                    logger.warning(f"DuckDuckGo搜索返回状态码: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"DuckDuckGo搜索错误: {str(e)}")
            return []
    
    def _parse_duckduckgo_results(self, html: str, num_results: int) -> List[SearchResult]:
        """解析DuckDuckGo搜索结果"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            # 查找搜索结果
            result_links = soup.find_all('a', class_='result__a')
            
            for link in result_links[:num_results]:
                try:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # 查找对应的摘要
                    snippet_element = link.find_next('a', class_='result__snippet')
                    snippet = snippet_element.get_text().strip() if snippet_element else ""
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source="duckduckgo"
                        ))
                except Exception as e:
                    logger.warning(f"解析搜索结果时出错: {str(e)}")
                    continue
            
            return results
        except Exception as e:
            logger.error(f"解析DuckDuckGo HTML时出错: {str(e)}")
            return []
    
    async def invoke(self, input_data: Dict[str, Any]) -> List[SearchResult]:
        """
        LangChain工具兼容的调用方法
        
        Args:
            input_data: 包含查询的字典
            
        Returns:
            搜索结果列表
        """
        query = input_data.get("query", "")
        if not query:
            logger.warning("搜索查询为空")
            return []
        
        return await self.search(query)
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()


# 创建全局搜索工具实例
search_tool = SearchTool()
