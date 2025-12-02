import aiohttp
import json
from typing import List, Dict
from .base_client import BaseLLMClient

class DeepSeekClient(BaseLLMClient):
    async def chat(self, messages: List[Dict[str, str]], model: str = None, search_whitelist: List[str] = None) -> str:
        """DeepSeek 异步聊天实现"""
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API调用失败: {response.status} - {error_text}")
                
                result = await response.json()
                return result["choices"][0]["message"]["content"]
