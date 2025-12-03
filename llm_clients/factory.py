
# llm_clients/factory.py
from typing import Dict, Any
from .base_client import BaseLLMClient
from .zhipu_client import ZhipuClient
from .deepseek_client import DeepSeekClient
from .gemini3_client import Gemini3Client
from config.manager import config_manager
import os

class LLMClientFactory:
    _clients = {
        'zhipu': ZhipuClient,
        'deepseek': DeepSeekClient,
        'gemini3': Gemini3Client,
    }
    
    @classmethod
    def create_client(cls, provider: str) -> BaseLLMClient:
        """创建LLM客户端实例"""
        if provider not in cls._clients:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        config = config_manager.get_llm_config(provider)
        if not config:
            raise ValueError(f"未找到提供商 {provider} 的配置")
        
        # 处理环境变量替换
        api_key = os.path.expandvars(config.get('api_key', ''))
        if not api_key or api_key.startswith('${'):
            raise ValueError(f"提供商 {provider} 的API_KEY未配置")
        
        client_class = cls._clients[provider]
        return client_class(
            api_key=api_key,
            base_url=config.get('base_url', ''),
            model=config.get('model', ''),
            temperature=config.get('temperature', 0.7),
            max_tokens=config.get('max_tokens', 1024)
        )
    
    @classmethod
    def register_client(cls, name: str, client_class: type):
        """注册新的LLM客户端"""
        cls._clients[name] = client_class
