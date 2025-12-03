# data_service.py
import random
import time
from typing import Dict, Any

def get_social_inventory_data(commodity_name: str) -> Dict[str, Any]:
    """
    模拟获取社会库存数据的接口
    在真实项目中，这里会是向外部API发起HTTP请求
    """
    print(f"--- [数据接口] 正在获取 {commodity_name} 的社会库存数据... ---")
    # 模拟API返回的数据
    mock_data = {
        "豆粕": {
            "total_inventory": 85.5,  # 万吨
            "weekly_change": -2.3,     # 环比变化
            "main_warehouses": {
                "日照港": 25.1,
                "天津港": 18.4,
                "张家港": 15.2
            }
        },
        "铜": {
            "total_inventory": 155203, # 吨
            "weekly_change": 8542,
            "main_warehouses": {
                "上海保税区": 55123,
                "广东保税区": 42101,
                "江苏保税区": 30105
            }
        }
    }

    # 模拟网络延迟
    import time
    time.sleep(1) 

    data = mock_data.get(commodity_name, {"error": f"未找到商品 {commodity_name} 的数据"})
    print(f"--- [数据接口] 数据获取成功: {data} ---")
    return data

def get_factory_inventory_data(commodity_name: str) -> Dict[str, Any]:
    """模拟获取工厂库存数据"""
    print(f"--- [数据接口] 正在获取 {commodity_name} 的工厂库存数据... ---")
    # ... 类似的模拟逻辑 ...
    time.sleep(1)
    data = {"factory_A": 5000, "factory_B": 6200, "operating_rate": "75%"}
    print(f"--- [数据接口] 数据获取成功: {data} ---")
    return data
