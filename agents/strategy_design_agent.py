# strategy_design_agent.py
from .base_agent import BaseAgent
from utils.prompt_loader import prompt_loader
import logging

logger = logging.getLogger(__name__)

class StrategyDesignAgent(BaseAgent):
    """策略设计Agent，专门生成结构化的期权策略"""
    
    def __init__(self, llm_provider: str = None):
        super().__init__(llm_provider)
        logger.info(f"初始化策略设计Agent，使用LLM: {self.llm_provider}")
    
    async def analyze(self, content: str, commodity_name: str, market_analysis_report: str, **kwargs) -> str:
        """
        设计结构化策略
        
        Args:
            commodity_name: 商品名称，如"豆粕"
            market_analysis_report: 来自OrchestratorAgent的综合分析报告
            
        Returns:
            结构化策略设计方案
        """
        self._validate_commodity_name(commodity_name)
        
        try:
            from datetime import datetime
            design_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"开始为 {commodity_name} 设计策略")
            
            market_analysis_report = content

            prompt = prompt_loader.format_prompt(
                "strategy_design", 
                commodity_name=commodity_name,
                design_time=design_time,
                market_analysis_report=market_analysis_report
            )
            messages = [{"role": "user", "content": prompt}]
            
            # 策略设计需要精确，可以关闭搜索，或只允许搜索金融术语
            result = await self.chat(messages, search_whitelist=["期权术语", "金融百科"])
            logger.info(f"{commodity_name} 策略设计完成")
            
            return result
        except Exception as e:
            logger.error(f"{commodity_name} 策略设计失败: {e}")
            raise
