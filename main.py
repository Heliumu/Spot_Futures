import asyncio
from llm_clients.factory import LLMClientFactory
from config.manager import config_manager

async def main():
    provider = "deepseek"  # 或 "deepseek"
    client = LLMClientFactory.create_client(provider)
    
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    
    response = await client.chat(messages)
    print(f"{provider} 回复: {response}")

if __name__ == "__main__":
    asyncio.run(main())
