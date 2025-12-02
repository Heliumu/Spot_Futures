import aiohttp
import json
from typing import List, Dict
from .base_client import BaseLLMClient

class ZhipuClient(BaseLLMClient):
    async def chat(self, messages: List[Dict[str, str]], model: str = None, search_whitelist: List[str] = None) -> str:
        """智谱AI聊天实现"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # 如果有搜索白名单，添加到payload中
        if search_whitelist:
            payload["tools"] = [{
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_whitelist": search_whitelist
                }
            }]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"智谱API调用失败: {response.status} - {error_text}")
                
                result = await response.json()
                return result["choices"][0]["message"]["content"]
