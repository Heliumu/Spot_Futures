from .base_agent import BaseAgent
from utils.prompt_loader import prompt_loader
import logging

logger = logging.getLogger(__name__)

class FactoryInventoryAnalysisAgent(BaseAgent):
    """工厂库存分析Agent"""
    
    def __init__(self, llm_provider: str = None):
        super().__init__(llm_provider)
        logger.info(f"初始化工厂库存分析Agent，使用LLM: {self.llm_provider}")
    
    async def analyze(self, content: str, commodity_name: str, **kwargs) -> str:
        self._validate_commodity_name(commodity_name)
        
        try:
            from datetime import datetime
            analysis_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"开始工厂库存分析，商品: {commodity_name}")
            
            prompt = prompt_loader.format_prompt(
                "factory_inventory_analysis", 
                commodity_name=commodity_name,
                analysis_time=analysis_time,
                factory_inventory_data=content
            )
            messages = [{"role": "user", "content": prompt}]
            
            result = await self.chat(messages, search_whitelist=["财经网站", "行业资讯网", "期货公司报告"]) # 允许搜索
            logger.info(f"{commodity_name} 工厂库存分析完成")
            
            return result
        except Exception as e:
            logger.error(f"{commodity_name} 工厂库存分析失败: {e}")
            raise
