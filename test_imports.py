def test_imports():
    """测试所有必需的模块导入"""
    try:
        import aiohttp
        print("✅ aiohttp 导入成功")
    except ImportError as e:
        print(f"❌ aiohttp 导入失败: {e}")
    
    try:
        import httpx
        print("✅ httpx 导入成功")
    except ImportError as e:
        print(f"❌ httpx 导入失败: {e}")
    
    try:
        import openai
        print("✅ openai 导入成功")
    except ImportError as e:
        print(f"❌ openai 导入失败: {e}")
    
    try:
        import pydantic
        print("✅ pydantic 导入成功")
    except ImportError as e:
        print(f"❌ pydantic 导入失败: {e}")
    
    try:
        import fastmcp
        print("✅ fastmcp 导入成功")
    except ImportError as e:
        print(f"❌ fastmcp 导入失败: {e}")
    
    try:
        import toml
        print("✅ toml 导入成功")
    except ImportError as e:
        print(f"❌ toml 导入失败: {e}")

if __name__ == "__main__":
    test_imports()
