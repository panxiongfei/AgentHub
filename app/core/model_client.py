"""
大模型客户端模块
提供统一的大模型调用接口，支持多种模型提供商
"""

import asyncio
import base64
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import aiohttp
from dataclasses import dataclass

from app.config.settings import get_settings
from app.core.logger import get_logger
from app.core.exceptions import AgentHubException


class ModelClientError(AgentHubException):
    """模型客户端异常"""
    pass


@dataclass
class ModelMessage:
    """模型消息"""
    role: str  # "user", "assistant", "system"
    content: Union[str, List[Dict[str, Any]]]  # 文本或多模态内容
    
    
@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    usage: Dict[str, int]
    model: str
    provider: str
    finish_reason: str = "stop"


class BaseModelClient:
    """基础模型客户端"""
    
    def __init__(self, config_section: Dict[str, Any]):
        self.config = config_section
        self.logger = get_logger(f"model.{self.__class__.__name__.lower()}")
        
    async def chat_completion(
        self,
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """聊天完成"""
        raise NotImplementedError
        
    async def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str = "请分析这张图片的内容",
        **kwargs
    ) -> ModelResponse:
        """分析图片"""
        # 读取图片
        image_data = await self._encode_image(image_path)
        
        # 构建多模态消息
        message = ModelMessage(
            role="user",
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
            ]
        )
        
        return await self.chat_completion([message], **kwargs)
    
    async def _encode_image(self, image_path: Union[str, Path]) -> str:
        """编码图片为base64"""
        image_path = Path(image_path)
        if not image_path.exists():
            raise ModelClientError(f"图片文件不存在: {image_path}")
            
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        return base64.b64encode(image_data).decode('utf-8')


class GeminiClient(BaseModelClient):
    """Google Gemini 客户端"""
    
    def __init__(self, config_section: Dict[str, Any]):
        super().__init__(config_section)
        self.api_key = config_section.get("api_key")
        self.model = config_section.get("model", "gemini-2.0-flash-exp")
        self.base_url = config_section.get("base_url", "https://generativelanguage.googleapis.com")
        
        if not self.api_key:
            raise ModelClientError("Gemini API key is required")
            
    async def chat_completion(
        self,
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """Gemini 聊天完成"""
        try:
            # 构建请求数据
            contents = self._build_gemini_contents(messages)
            
            request_data = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": kwargs.get("max_tokens", self.config.get("max_tokens", 4000)),
                    "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                }
            }
            
            # 构建请求URL
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent"
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key
                    },
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 30))
                ) as response:
                    response_data = await response.json()
                    
                    if response.status != 200:
                        error_msg = response_data.get("error", {}).get("message", "Unknown error")
                        raise ModelClientError(f"Gemini API error: {error_msg}")
                    
                    return self._parse_gemini_response(response_data)
                    
        except aiohttp.ClientError as e:
            raise ModelClientError(f"网络请求失败: {e}")
        except Exception as e:
            self.logger.error(f"Gemini API调用失败: {e}")
            raise ModelClientError(f"调用失败: {e}")
    
    def _build_gemini_contents(self, messages: List[ModelMessage]) -> List[Dict[str, Any]]:
        """构建Gemini格式的内容"""
        contents = []
        
        for message in messages:
            if isinstance(message.content, str):
                # 纯文本消息
                contents.append({
                    "role": "user" if message.role == "user" else "model",
                    "parts": [{"text": message.content}]
                })
            else:
                # 多模态消息
                parts = []
                for item in message.content:
                    if item["type"] == "text":
                        parts.append({"text": item["text"]})
                    elif item["type"] == "image_url":
                        # 处理base64图片
                        image_data = item["image_url"]["url"]
                        if image_data.startswith("data:"):
                            # 提取base64数据
                            _, base64_data = image_data.split(",", 1)
                            parts.append({
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": base64_data
                                }
                            })
                
                contents.append({
                    "role": "user" if message.role == "user" else "model",
                    "parts": parts
                })
        
        return contents
    
    def _parse_gemini_response(self, response_data: Dict[str, Any]) -> ModelResponse:
        """解析Gemini响应"""
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                raise ModelClientError("No response candidates found")
            
            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                raise ModelClientError("No content parts found")
            
            text_content = parts[0].get("text", "")
            
            # 获取使用统计
            usage_metadata = response_data.get("usageMetadata", {})
            usage = {
                "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                "total_tokens": usage_metadata.get("totalTokenCount", 0)
            }
            
            return ModelResponse(
                content=text_content,
                usage=usage,
                model=self.model,
                provider="gemini",
                finish_reason=candidate.get("finishReason", "stop").lower()
            )
            
        except Exception as e:
            raise ModelClientError(f"解析Gemini响应失败: {e}")


class DeepSeekClient(BaseModelClient):
    """DeepSeek 客户端"""
    
    def __init__(self, config_section: Dict[str, Any]):
        super().__init__(config_section)
        self.api_key = config_section.get("api_key")
        self.model = config_section.get("model", "deepseek-chat")
        self.base_url = config_section.get("base_url", "https://api.deepseek.com")
        
        if not self.api_key:
            raise ModelClientError("DeepSeek API key is required")
            
    async def chat_completion(
        self,
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """DeepSeek 聊天完成"""
        try:
            # 构建请求数据
            request_messages = self._build_deepseek_messages(messages)
            
            request_data = {
                "model": self.model,
                "messages": request_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                "stream": False
            }
            
            # 构建请求URL
            url = f"{self.base_url}/chat/completions"
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 30))
                ) as response:
                    response_data = await response.json()
                    
                    if response.status != 200:
                        error_msg = response_data.get("error", {}).get("message", "Unknown error")
                        raise ModelClientError(f"DeepSeek API error: {error_msg}")
                    
                    return self._parse_deepseek_response(response_data)
                    
        except aiohttp.ClientError as e:
            raise ModelClientError(f"网络请求失败: {e}")
        except Exception as e:
            self.logger.error(f"DeepSeek API调用失败: {e}")
            raise ModelClientError(f"调用失败: {e}")
    
    def _build_deepseek_messages(self, messages: List[ModelMessage]) -> List[Dict[str, Any]]:
        """构建DeepSeek格式的消息"""
        request_messages = []
        
        for message in messages:
            if isinstance(message.content, str):
                # 纯文本消息
                request_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            else:
                # 多模态消息 - DeepSeek目前不支持图片，但我们可以提取文本部分
                text_content = ""
                for item in message.content:
                    if item["type"] == "text":
                        text_content += item["text"]
                    elif item["type"] == "image_url":
                        # DeepSeek暂不支持图片，记录警告
                        self.logger.warning("DeepSeek API暂不支持图片分析，将忽略图片内容")
                
                if text_content:
                    request_messages.append({
                        "role": message.role,
                        "content": text_content
                    })
        
        return request_messages
    
    def _parse_deepseek_response(self, response_data: Dict[str, Any]) -> ModelResponse:
        """解析DeepSeek响应"""
        try:
            choices = response_data.get("choices", [])
            if not choices:
                raise ModelClientError("No response choices found")
            
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # 获取使用统计
            usage = response_data.get("usage", {})
            usage_dict = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
            
            return ModelResponse(
                content=content,
                usage=usage_dict,
                model=response_data.get("model", self.model),
                provider="deepseek",
                finish_reason=choice.get("finish_reason", "stop")
            )
            
        except Exception as e:
            raise ModelClientError(f"解析DeepSeek响应失败: {e}")
    
    async def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str = "请分析这张图片的内容",
        **kwargs
    ) -> ModelResponse:
        """分析图片 - DeepSeek目前不支持图片分析"""
        # DeepSeek目前不支持图片分析，返回提示信息
        self.logger.warning("DeepSeek API暂不支持图片分析功能")
        
        fallback_message = ModelMessage(
            role="user",
            content=f"抱歉，DeepSeek模型暂不支持图片分析功能。请求的图片路径：{image_path}，提示：{prompt}"
        )
        
        return await self.chat_completion([fallback_message], **kwargs)


class ModelClientManager:
    """模型客户端管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("model.manager")
        self._clients = {}
        
    def get_client(self, provider: Optional[str] = None) -> BaseModelClient:
        """获取模型客户端"""
        provider = provider or self.settings.model.default_provider
        
        if provider not in self._clients:
            self._clients[provider] = self._create_client(provider)
            
        return self._clients[provider]
    
    def _create_client(self, provider: str) -> BaseModelClient:
        """创建模型客户端"""
        if provider.lower() == "gemini":
            config = {
                "api_key": self.settings.model.gemini_api_key,
                "model": self.settings.model.gemini_model,
                "base_url": self.settings.model.gemini_base_url,
                "max_tokens": self.settings.model.max_tokens,
                "temperature": self.settings.model.temperature,
                "timeout": self.settings.model.timeout
            }
            return GeminiClient(config)
        elif provider.lower() == "deepseek":
            config = {
                "api_key": self.settings.model.deepseek_api_key,
                "model": self.settings.model.default_model,
                "base_url": self.settings.model.deepseek_base_url,
                "max_tokens": self.settings.model.max_tokens,
                "temperature": self.settings.model.temperature,
                "timeout": self.settings.model.timeout
            }
            return DeepSeekClient(config)
        else:
            raise ModelClientError(f"不支持的模型提供商: {provider}")
    
    async def chat_completion(
        self,
        messages: Union[List[ModelMessage], List[Dict[str, str]]],
        provider: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """聊天完成（简化接口）"""
        # 转换消息格式
        if messages and isinstance(messages[0], dict):
            messages = [ModelMessage(role=msg["role"], content=msg["content"]) for msg in messages]
        
        client = self.get_client(provider)
        return await client.chat_completion(messages, **kwargs)
    
    async def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str = "请分析这张图片的内容",
        provider: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """分析图片（简化接口）"""
        client = self.get_client(provider)
        return await client.analyze_image(image_path, prompt, **kwargs)
    
    async def summarize_text(
        self,
        text: str,
        prompt_template: str = "请对以下内容进行总结概括，提取关键信息：\n\n{text}",
        provider: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """文本总结（便捷方法）"""
        prompt = prompt_template.format(text=text[:8000])  # 限制长度
        
        messages = [ModelMessage(role="user", content=prompt)]
        return await self.chat_completion(messages, provider, **kwargs)


# 全局模型客户端管理器实例
_model_manager = None

def get_model_client() -> ModelClientManager:
    """获取全局模型客户端管理器"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelClientManager()
    return _model_manager 