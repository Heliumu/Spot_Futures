# test_agent.py
import asyncio
import logging
from agents import (
    BasisAnalysisAgent, 
    MacroEconomicAgent, 
    IndustryFundamentalsAgent,
    PriceAnalysisAgent,
    FactoryInventoryAnalysisAgent,
    SocialInventoryAnalysisAgent,
    OrchestratorAgent,
    StrategyDesignAgent
)
from config.manager import config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_individual_agents():
    """测试各个Agent"""
    default_llm = config_manager.get('agents', 'default_llm', 'zhipu')
    
    # 测试内容
    test_content = """
    市场情况：
    - 现货价格：3200元/吨
    - 主力合约价格：3150元/吨
    - 基差：50元/吨（升水）
    - 库存：80万吨，环比下降8%
    """
    
    commodity = "豆粕"
    
    # 测试各个Agent
    agents = {
        "基差分析": BasisAnalysisAgent(default_llm),
        "宏观经济": MacroEconomicAgent(default_llm),
        "产业基本面": IndustryFundamentalsAgent(default_llm),
        "价格分析": PriceAnalysisAgent(default_llm),
        "工厂库存分析": FactoryInventoryAnalysisAgent(default_llm),
        "社会库存分析": SocialInventoryAnalysisAgent(default_llm),
        "策略设计": StrategyDesignAgent(default_llm),
    }
    
    for name, agent in agents.items():
        try:
            print(f"\n=== {name} ===")
            result = await agent.analyze(test_content, commodity)
            print(result[:200] + "..." if len(result) > 200 else result)
        except Exception as e:
            print(f"错误: {e}")

async def test_orchestrator():
    """测试主控Agent"""
    default_llm = config_manager.get('agents', 'default_llm', 'zhipu')
    orchestrator = OrchestratorAgent(default_llm)
    
    test_content = """
    豆粕市场情况：
    - 现货价格：3200元/吨
    - 主力合约价格：3150元/吨
    - 基差：50元/吨（升水）
    - 港口库存：80万吨，环比下降8%
    - 需求：生猪养殖利润回升，饲料需求预期增加
    """
    # test_content = """
    # 找到豆粕市场最新动态
    # """
    
    try:
        print("\n=== 综合分析 ===")
        result = await orchestrator.comprehensive_analysis(test_content, "豆粕")
        for analysis_type, content in result.items():
            print(f"\n【{analysis_type.upper()}】")
            print(content[:200] + "..." if len(content) > 200 else content)
    except Exception as e:
        print(f"错误: {e}")

async def test_validation():
    """测试商品名称验证"""
    default_llm = config_manager.get('agents', 'default_llm', 'zhipu')
    agent = BasisAnalysisAgent(default_llm)
    
    # 测试空商品名称
    try:
        await agent.analyze("测试内容", "")
    except ValueError as e:
        print(f"\n空商品名称测试通过: {e}")
    
    # 测试正常商品名称
    try:
        result = await agent.analyze("测试内容", "豆粕")
        print(f"\n正常商品名称测试通过")
    except Exception as e:
        print(f"错误: {e}")

async def main():
    """主测试函数"""
    print("开始测试Agent...")
    
    # 测试商品名称验证
    # await test_validation()
    
    # 测试各个Agent
    await test_individual_agents()
    
    # 测试主控Agent
    await test_orchestrator()
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
