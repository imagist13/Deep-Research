"""
LLM基类定义
提供统一的LLM接口
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLM(ABC):
    """LLM基类，定义统一的接口"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化LLM
        
        Args:
            api_key: API密钥
            model_name: 模型名称
        """
        self.api_key = api_key
        self.model_name = model_name
    
    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        pass
    
    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用LLM生成回复
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            **kwargs: 其他参数
            
        Returns:
            LLM生成的回复文本
        """
        pass
    
    def validate_response(self, response: str) -> str:
        """
        验证和清理响应
        
        Args:
            response: 原始响应
            
        Returns:
            清理后的响应
        """
        if not response or not response.strip():
            return "抱歉，我无法生成有效的回复。"
        return response.strip()
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        pass
