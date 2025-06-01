"""
增强版Skywork平台实现
使用智能浏览器引擎进行页面操作
"""

from typing import Dict, List, Any

from app.platforms.enhanced_platform_base import EnhancedPlatformBase


class EnhancedSkyworkPlatform(EnhancedPlatformBase):
    """增强版Skywork平台实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("skywork", config)
    
    def _get_platform_selectors(self) -> Dict[str, List[str]]:
        """获取Skywork平台特定的选择器配置"""
        return {
            "input": [
                # Skywork特有的输入框选择器
                'textarea[placeholder*="输入"]',
                'textarea[placeholder*="请输入"]',
                'textarea[placeholder*="问题"]',
                'textarea[placeholder*="内容"]',
                'textarea[placeholder*="想问"]',
                'textarea[placeholder*="想了解"]',
                'textarea[placeholder*="chat"]',
                'textarea[placeholder*="message"]',
                'div[contenteditable="true"][data-placeholder*="输入"]',
                'div[contenteditable="true"][placeholder*="输入"]',
                '.chat-input textarea',
                '.message-input textarea',
                '.question-input',
                '.prompt-input',
                '.skywork-input',
                '.ai-input',
                # 通用输入框
                'input[type="text"][placeholder*="输入"]',
                'textarea',
                'div[contenteditable="true"]',
                'input[type="text"]'
            ],
            "submit": [
                # Skywork特有的提交按钮
                'button:has-text("发送")',
                'button:has-text("提交")',
                'button:has-text("确定")',
                'button:has-text("开始")',
                'button:has-text("提问")',
                'button:has-text("询问")',
                'button:has-text("搜索")',
                'button:has-text("chat")',
                'button:has-text("send")',
                'button[aria-label*="发送"]',
                'button[aria-label*="提交"]',
                'button[aria-label*="submit"]',
                'button[data-action="send"]',
                'button[data-action="submit"]',
                '.send-button',
                '.submit-button',
                '.chat-send',
                '.message-send',
                '.ask-button',
                '.query-button',
                # 通用提交按钮
                'button[type="submit"]',
                'input[type="submit"]'
            ],
            "loading": [
                # Skywork特有的加载指示器
                '.loading',
                '.spinner',
                '.dots-loading',
                '.generating',
                '.thinking',
                '.processing',
                '.typing',
                '.ai-thinking',
                '.skywork-loading',
                '.chat-loading',
                '.message-loading',
                '[data-loading="true"]',
                '[data-status="generating"]',
                '[data-status="thinking"]',
                '[data-status="processing"]',
                '[class*="loading"]',
                '[class*="spinner"]',
                '[class*="dots"]',
                '[class*="progress"]'
            ],
            "content": [
                # Skywork特有的内容选择器
                '.message',
                '.response',
                '.result',
                '.answer',
                '.output',
                '.reply',
                '.generated-content',
                '.chat-message',
                '.ai-message',
                '.assistant-message',
                '.skywork-response',
                '.ai-response',
                '.bot-message',
                '.conversation-message',
                '.chat-content',
                '.message-content',
                '.response-content',
                # 通用内容选择器
                '.content',
                '.text',
                'article',
                'main',
                '.main-content',
                '[role="main"]',
                '[data-message-type="assistant"]',
                '[data-role="assistant"]'
            ],
            "error": [
                # Skywork特有的错误指示器
                '.error',
                '.failed',
                '.warning',
                '.alert',
                '.insufficient',
                '.limit-exceeded',
                '.quota-exceeded',
                '.rate-limit',
                '.skywork-error',
                '.api-error',
                '.system-error',
                '[role="alert"]',
                '[data-status="error"]',
                '[data-status="failed"]',
                '[class*="error"]',
                '[class*="fail"]',
                '[class*="warning"]',
                '[class*="alert"]'
            ]
        }
    
    def _get_platform_keywords(self) -> Dict[str, List[str]]:
        """获取Skywork平台特定的关键词配置"""
        return {
            "title": [
                "skywork",
                "天工",
                "ai助手",
                "智能助手",
                "chat",
                "对话",
                "问答"
            ],
            "input_placeholder": [
                "输入",
                "请输入",
                "问题",
                "内容",
                "想问",
                "想了解",
                "chat",
                "message"
            ],
            "submit_text": [
                "发送",
                "提交", 
                "确定",
                "开始",
                "提问",
                "询问",
                "搜索",
                "send",
                "submit"
            ],
            "loading_indicators": [
                "正在生成",
                "思考中",
                "处理中",
                "加载中",
                "generating",
                "thinking",
                "processing",
                "loading"
            ],
            "error_keywords": [
                "积分不足",
                "余额不足",
                "次数用完",
                "限制",
                "错误",
                "失败",
                "error",
                "failed",
                "insufficient",
                "limit",
                "quota"
            ]
        }
    
    def _get_platform_domains(self) -> List[str]:
        """获取Skywork平台域名列表"""
        return [
            "skywork.ai",
            "tiangong.cn",
            "kunlun.ai"
        ] 