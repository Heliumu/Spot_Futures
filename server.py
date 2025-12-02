from fastmcp import FastMCP
from agents.orchestrator_agent import OrchestratorAgent
from config.manager import config_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastMCP服务器
mcp = FastMCP("期货分析Agent服务器")

# 获取默认LLM提供商
default_llm = config_manager.get('agents', 'default_llm', 'zhipu')
orchestrator = OrchestratorAgent(default_llm)

@mcp.tool()
async def basis_analysis(content: str) -> str:
    """基差分析"""
    try:
        result = await orchestrator.single_analysis('basis', content)
        return f"基差分析结果:\n{result}"
    except Exception as e:
        logger.error(f"基差分析失败: {e}")
        return f"分析失败: {str(e)}"

@mcp.tool()
async def macro_economic_analysis(content: str) -> str:
    """宏观经济分析"""
    try:
        result = await orchestrator.single_analysis('macro', content)
        return f"宏观经济分析结果:\n{result}"
    except Exception as e:
        logger.error(f"宏观经济分析失败: {e}")
        return f"分析失败: {str(e)}"

@mcp.tool()
async def industry_fundamentals_analysis(content: str) -> str:
    """产业基本面分析"""
    try:
        result = await orchestrator.single_analysis('industry', content)
        return f"产业基本面分析结果:\n{result}"
    except Exception as e:
        logger.error(f"产业基本面分析失败: {e}")
        return f"分析失败: {str(e)}"

@mcp.tool()
async def price_analysis(content: str) -> str:
    """价格技术分析"""
    try:
        result = await orchestrator.single_analysis('price', content)
        return f"价格技术分析结果:\n{result}"
    except Exception as e:
        logger.error(f"价格技术分析失败: {e}")
        return f"分析失败: {str(e)}"

@mcp.tool()
async def comprehensive_analysis(content: str, analysis_types: str = "basis,macro,industry,price") -> dict:
    """
    综合分析
    
    Args:
        content: 待分析的内容
        analysis_types: 分析类型，逗号分隔，可选: basis,macro,industry,price
    """
    try:
        types_list = [t.strip() for t in analysis_types.split(',') if t.strip()]
        result = await orchestrator.comprehensive_analysis(content, types_list)
        
        return {
            "status": "success",
            "analysis_types": types_list,
            "results": result
        }
    except Exception as e:
        logger.error(f"综合分析失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def get_analysis_types() -> list:
    """获取支持的分析类型"""
    return orchestrator.get_supported_analysis_types()

if __name__ == "__main__":
    debug_enabled = config_manager.get('debug', 'enabled', True)
    if debug_enabled:
        logger.info("启动调试模式，可通过 MCP Inspector 访问")
    
    mcp.run(transport='stdio')
