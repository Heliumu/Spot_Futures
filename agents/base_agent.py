# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from llm_clients.factory import LLMClientFactory
from config.manager import config_manager
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """所有Agent的基类，提供通用的LLM客户端管理功能"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        初始化Agent
        
        Args:
            llm_provider: 指定LLM提供商，如果不提供则从配置读取默认值
        """
        self.llm_provider = llm_provider or self._get_default_llm_provider()
        logger.info(f"初始化 Agent，使用LLM提供商: {self.llm_provider}")
        
        try:
            self.llm_client = LLMClientFactory.create_client(self.llm_provider)
            logger.info(f"成功为 Agent 创建LLM客户端: {self.llm_provider}")
        except Exception as e:
            logger.error(f"创建LLM客户端失败: {e}")
            raise

    def _get_default_llm_provider(self) -> str:
        """获取默认的LLM提供商"""
        try:
            default_provider = config_manager.get('llm', 'default_provider')
            if default_provider:
                return default_provider
            logger.warning("未找到全局默认LLM提供商，使用 'zhipu' 作为默认值")
            return "zhipu"
        except Exception as e:
            logger.warning(f"获取默认LLM提供商时出错: {e}，使用 'zhipu' 作为默认值")
            return "zhipu"

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        使用LLM客户端进行对话
        
        Args:
            messages: 对话消息列表
            **kwargs: 其他传递给LLM客户端的参数
            
        Returns:
            LLM的回复内容
        """
        try:
            return await self.llm_client.chat(messages, **kwargs)
        except Exception as e:
            logger.error(f"LLM对话时发生错误: {e}")
            raise

    def _validate_commodity_name(self, commodity_name: str):
        """
        验证商品名称（改为普通方法，不是抽象方法）
        
        Args:
            commodity_name: 商品名称
            
        Raises:
            ValueError: 如果商品名称为空或无效
        """
        if not commodity_name or not commodity_name.strip():
            raise ValueError(
                "商品名称不能为空。请提供具体的商品名称，如：豆粕、铜、原油等。"
            )

    @abstractmethod
    async def analyze(self, content: str, commodity_name: str, **kwargs) -> str:
        """
        执行分析，必须提供商品名称
        
        Args:
            content: 待分析的内容
            commodity_name: 商品名称，如"豆粕"、"铜"、"原油"
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        pass
