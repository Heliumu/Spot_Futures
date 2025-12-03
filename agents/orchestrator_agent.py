# agents/orchestrator_agent.py
from typing import List, Dict, Optional
from .base_agent import BaseAgent
from .basis_analysis_agent import BasisAnalysisAgent
from .macro_economic_agent import MacroEconomicAgent
from .industry_fundamentals_agent import IndustryFundamentalsAgent
from .price_analysis_agent import PriceAnalysisAgent
from .factory_inventory_analysis_agent import FactoryInventoryAnalysisAgent # 新增
from .social_inventory_analysis_agent import SocialInventoryAnalysisAgent   # 新增
from .strategy_design_agent import StrategyDesignAgent
from utils.prompt_loader import prompt_loader
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    """主控Agent，协调所有分析Agent"""
    
    def __init__(self, llm_provider: str = None):
        super().__init__(llm_provider)
        logger.info(f"初始化主控Agent，使用LLM: {self.llm_provider}")
        
        # 初始化所有分析Agent
        self.basis_agent = BasisAnalysisAgent(llm_provider)
        self.macro_agent = MacroEconomicAgent(llm_provider)
        self.industry_agent = IndustryFundamentalsAgent(llm_provider)
        self.price_agent = PriceAnalysisAgent(llm_provider)
        self.factory_agent = FactoryInventoryAnalysisAgent(llm_provider) 
        self.social_agent = SocialInventoryAnalysisAgent(llm_provider)   
        self.strategy_agent = StrategyDesignAgent(llm_provider)
    
    async def analyze(self, content: str, commodity_name: str, **kwargs) -> str:
        """
        执行综合分析（重写基类的抽象方法）
        
        Args:
            content: 待分析的内容
            commodity_name: 商品名称
            
        Returns:
            综合分析报告
        """
        # 验证商品名称
        self._validate_commodity_name(commodity_name)
        
        # 执行综合分析
        result = await self.comprehensive_analysis(content, commodity_name)
        
        # 返回综合分析结果
        return result.get('comprehensive', '综合分析生成失败')
    
    async def comprehensive_analysis(
        self, 
        content: str,
        commodity_name: str,
        analysis_types: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        执行综合分析
        
        Args:
            content: 待分析的内容
            commodity_name: 商品名称，如"豆粕"、"铜"
            analysis_types: 要执行的分析类型列表，默认执行所有分析
            
        Returns:
            包含所有分析结果的字典
        """
        # 验证商品名称
        self._validate_commodity_name(commodity_name)
        
        # 默认执行所有分析
        if analysis_types is None:
            analysis_types = ['basis', 'macro', 'industry', 'price', 'factory', 'social', 'strategy_design']
        
        logger.info(f"开始 {commodity_name} 综合分析，执行类型: {', '.join(analysis_types)}")
        
        # 构建分析任务
        tasks = []
        task_names = []
        
        if 'basis' in analysis_types:
            tasks.append(self.basis_agent.analyze(content, commodity_name))
            task_names.append('basis')
        
        if 'macro' in analysis_types:
            tasks.append(self.macro_agent.analyze(content, commodity_name))
            task_names.append('macro')
        
        if 'industry' in analysis_types:
            tasks.append(self.industry_agent.analyze(content, commodity_name))
            task_names.append('industry')
        
        if 'price' in analysis_types:
            tasks.append(self.price_agent.analyze(content, commodity_name))
            task_names.append('price')
        
        if 'factory' in analysis_types:
            tasks.append(self.factory_agent.analyze(content, commodity_name))
            task_names.append('factory')
        
        if 'social' in analysis_types:
            tasks.append(self.social_agent.analyze(content, commodity_name))
            task_names.append('social')
        
        # if 'strategy_design' in analysis_types:
        #     tasks.append(self.strategy_agent.analyze(commodity_name, content, market_analysis_report=analysis_results))
        #     task_names.append('strategy_design')
        
        # 并行执行分析
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        analysis_results = {}
        for i, (name, result) in enumerate(zip(task_names, results)):
            if isinstance(result, Exception):
                logger.error(f"{commodity_name} {name}分析失败: {result}")
                analysis_results[name] = f"分析失败: {str(result)}"
            else:
                analysis_results[name] = result
                logger.info(f"{commodity_name} {name}分析完成")
        
        # 生成综合分析
        try:
            comprehensive_result = await self._generate_comprehensive_analysis(
                analysis_results, commodity_name
            )
            analysis_results['comprehensive'] = comprehensive_result
            logger.info(f"{commodity_name} 综合分析生成完成")
        except Exception as e:
            logger.error(f"{commodity_name} 综合分析生成失败: {e}")
            analysis_results['comprehensive'] = f"综合分析生成失败: {str(e)}"
        
        try:
            strategy_designer = StrategyDesignAgent(self.llm_provider)
            # 将完整的分析报告作为输入
            full_report = "\n\n".join(
                [f"===== {key.upper()} ANALYSIS =====\n{value}" for key, value in analysis_results.items()]
            )
            # 修正调用：提供所有必需的参数
            strategy_result = await strategy_designer.analyze(
                content=full_report, 
                commodity_name=commodity_name, 
                market_analysis_report=full_report
            )
            analysis_results['strategy_design'] = strategy_result
            logger.info(f"{commodity_name} 结构化策略设计完成")
        except Exception as e:
            logger.error(f"{commodity_name} 策略设计失败: {e}")
            analysis_results['strategy_design'] = f"策略设计失败: {str(e)}"
        # ==================================================

        return analysis_results
    
    async def _generate_comprehensive_analysis(
        self, 
        analysis_results: Dict[str, str], 
        commodity_name: str
    ) -> str:
        """
        生成综合分析报告
        
        Args:
            analysis_results: 各个分析的结果
            commodity_name: 商品名称
            
        Returns:
            综合分析报告
        """
        orchestrator_prompt = prompt_loader.format_prompt(
            "orchestrator",
            commodity_name=commodity_name,
            basis_analysis=analysis_results.get('basis', '未执行基差分析'),
            macro_economic=analysis_results.get('macro', '未执行宏观经济分析'),
            industry_fundamentals=analysis_results.get('industry', '未执行产业基本面分析'),
            price_analysis=analysis_results.get('price', '未执行价格分析'),
            factory_inventory=analysis_results.get('factory', '未执行工厂库存分析'),
            social_inventory=analysis_results.get('social', '未执行社会库存分析'),
            strategy_design=analysis_results.get('strategy_design', '未执行策略设计')
        )
        
        messages = [{"role": "user", "content": orchestrator_prompt}]
        return await self.chat(messages)
    
    async def single_analysis(self, analysis_type: str, content: str, commodity_name: str) -> str:
        """
        执行单一类型的分析
        
        Args:
            analysis_type: 分析类型 ('basis', 'macro', 'industry', 'price')
            content: 待分析的内容
            commodity_name: 商品名称
            
        Returns:
            分析结果
        """
        agent_map = {
            'basis': self.basis_agent,
            'macro': self.macro_agent,
            'industry': self.industry_agent,
            'price': self.price_agent,
            'factory': self.factory_agent,
            'social': self.social_agent,
            'strategy_design': self.strategy_agent,
        }
        
        if analysis_type not in agent_map:
            raise ValueError(f"不支持的分析类型: {analysis_type}")
        
        agent = agent_map[analysis_type]
        return await agent.analyze(content, commodity_name)
    
    def get_supported_analysis_types(self) -> List[str]:
        """获取支持的分析类型列表"""
        return ['basis', 'macro', 'industry', 'price', 'factory', 'social', 'strategy_design']
