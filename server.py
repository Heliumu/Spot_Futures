# server.py

import asyncio
import traceback
from datetime import datetime
from typing import List

# 使用 FastMCP 库，这是 fastmcp 工具推荐的现代用法
from fastmcp import FastMCP

# 导入我们项目中的模块
# 注意：这里的导入路径要和你项目中的实际路径匹配
from agents import OrchestratorAgent
from config.manager import config_manager

# 1. 实例化 FastMCP 服务器
#    "commodity-analysis-server" 是你的服务器名称，会显示在 inspector 中
mcp = FastMCP("commodity-analysis-server")

# ==============================================================================
#  工具类别: [智能分析]
# ==============================================================================

@mcp.tool()
async def comprehensive_analysis(
    commodity_name: str,
    content: str = "",
    analysis_types: List[str] = ["basis", "macro", "industry", "price", "factory", "social", "strategy_design"]
) -> str:
    """
    [分析] 对指定商品进行全面分析，包括基差、宏观、产业基本面和价格分析。

    Args:
        commodity_name: 商品名称，例如：豆粕、铜、原油。
        content: 用于分析的市场数据、新闻或文本内容。如果为空，Agent将尝试通过网络搜索获取信息。
        analysis_types: 指定要执行的分析类型列表，可选值: ["basis", "macro", "industry", "price", "factory", "social", "strategy_design"]。默认执行所有类型。
    """
    try:
        if not commodity_name or not commodity_name.strip():
            return "错误：'commodity_name' 参数不能为空。"

        # 从配置中获取默认的LLM提供商来初始化Orchestrator
        default_llm = config_manager.get('agents', 'default_llm', 'zhipu')
        orchestrator = OrchestratorAgent(llm_provider=default_llm)

        # 如果用户没有提供分析内容，则构造一个让模型去搜索的提示
        if not content or not content.strip():
            content = f"请自行搜索关于{commodity_name}的最新市场信息，并进行分析。"

        # 调用 orchestrator 的核心方法
        results = await orchestrator.comprehensive_analysis(
            content=content,
            commodity_name=commodity_name,
            analysis_types=analysis_types
        )
        
        # 将返回的结果字典格式化为更易读的字符串
        output_parts = []
        for key, value in results.items():
            output_parts.append(f"===== {key.upper()} ANALYSIS =====\n{value}")
        
        return "\n\n".join(output_parts)

    except Exception as e:
        # 捕获所有异常，并返回详细的错误信息，方便调试
        error_details = f"综合分析过程中发生错误: {type(e).__name__} - {e}\n--- 详细错误信息 ---\n{traceback.format_exc()}"
        return error_details


@mcp.tool()
async def single_analysis(
    analysis_type: str,
    commodity_name: str,
    content: str = ""
) -> str:
    """
    [分析] 对指定商品进行单一维度的分析。

    Args:
        analysis_type: 分析类型，可选值: "basis":基差分析, "macro":宏观分析, "industry":产业基本面分析, "price":价格分析, "factory":工厂分析, "social":社会分析, "strategy_design":策略设计。
        commodity_name: 商品名称，例如：豆粕。
        content: 用于分析的内容。如果为空，Agent将尝试通过网络搜索获取信息。
    """
    try:
        if not analysis_type or not analysis_type.strip():
            return "错误：'analysis_type' 参数不能为空。"
        if not commodity_name or not commodity_name.strip():
            return "错误：'commodity_name' 参数不能为空。"
        
        valid_types = ["basis", "macro", "industry", "price", "factory", "social", "strategy_design"]
        if analysis_type not in valid_types:
            return f"错误：无效的 'analysis_type'。可选值为: {', '.join(valid_types)}"

        # 从配置中获取默认的LLM提供商来初始化Orchestrator
        default_llm = config_manager.get('agents', 'default_llm', 'zhipu')
        orchestrator = OrchestratorAgent(llm_provider=default_llm)

        # 如果用户没有提供分析内容，则构造一个让模型去搜索的提示
        if not content or not content.strip():
            content = f"请自行搜索关于{commodity_name}的{analysis_type}相关信息，并进行分析。"

        # 调用 orchestrator 的单一分析方法
        result = await orchestrator.single_analysis(
            analysis_type=analysis_type,
            content=content,
            commodity_name=commodity_name
        )
        
        return result

    except Exception as e:
        error_details = f"单一分析过程中发生错误: {type(e).__name__} - {e}\n--- 详细错误信息 ---\n{traceback.format_exc()}"
        return error_details


# ==============================================================================
#  启动服务器
# ==============================================================================

if __name__ == "__main__":
    # 在stdio上运行服务器，这是 fastmcp inspector 的标准连接方式
    mcp.run(transport="stdio")
