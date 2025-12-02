# llm_clients/base_client.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMClient(ABC):
    """所有LLM客户端的抽象基类"""
    def __init__(self, api_key: str, base_url: str, model: str, **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.enable_search = kwargs.get('enable_search', False) # 是否启用搜索功能 新功能
        # 将其他参数如 temperature, max_tokens 存储起来
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 1024)

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], model: str = None, search_whitelist: List[str] = None) -> str: #  新增 search_whitelist 参数
        """
        与模型进行异步对话的抽象方法
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            model: 可选，指定使用的模型，如果不提供则使用默认模型
            
        Returns:
            模型的回复文本
            
        Raises:
            ValueError: 如果模型未配置或不支持搜索功能
        """
        pass
