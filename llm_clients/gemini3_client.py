import aiohttp
import json
from typing import List, Dict
from .base_client import BaseLLMClient

class Gemini3Client(BaseLLMClient):
    async def chat(self, messages: List[Dict[str, str]], model: str = None, search_whitelist: List[str] = None) -> str:
        """Gemini 1.5 Flash 异步聊天实现"""
        url = f"{self.base_url}/v1beta/models/{model or self.model}:generateContent?key={self.api_key}"
        
        headers = {"Content-Type": "application/json"}
        
        # 转换消息格式为 Gemini API 所需格式
        contents = []
        for msg in messages:
            contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API调用失败: {response.status} - {error_text}")
                
                result = await response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
