from typing import List, Dict
from .base_agent import BaseAgent
from utils.prompt_loader import prompt_loader
import logging

logger = logging.getLogger(__name__)

class BasisAnalysisAgent(BaseAgent):
    """基差分析Agent"""
    
    def __init__(self, llm_provider: str = None):
        super().__init__(llm_provider)
        logger.info(f"初始化基差分析Agent，使用LLM: {self.llm_provider}")
    
    async def analyze(self, content: str, commodity_name: str, **kwargs) -> str:
        """
        执行基差分析
        
        Args:
            content: 待分析的内容
            commodity_name: 商品名称，如"豆粕"、"铜"
            
        Returns:
            基差分析报告
        """
        # 验证商品名称（调用父类的验证方法）
        self._validate_commodity_name(commodity_name)
        
        try:
            logger.info(f"开始基差分析，商品: {commodity_name}，内容长度: {len(content)}")
            
            prompt = prompt_loader.format_prompt(
                "basis_analysis", 
                commodity_name=commodity_name,
                content=content
            )
            messages = [{"role": "user", "content": prompt}]
            
            result = await self.chat(messages)
            logger.info(f"{commodity_name} 基差分析完成")
            
            return result
        except Exception as e:
            logger.error(f"{commodity_name} 基差分析失败: {e}")
            raise
