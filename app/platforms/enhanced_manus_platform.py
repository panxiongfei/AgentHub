"""
增强版Manus平台实现
使用智能浏览器引擎进行页面操作
"""

from typing import Dict, List, Any

from app.platforms.enhanced_platform_base import EnhancedPlatformBase


class EnhancedManusPlatform(EnhancedPlatformBase):
    """增强版Manus平台实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("manus", config)
    
    def _get_platform_selectors(self) -> Dict[str, List[str]]:
        """获取Manus平台特定的选择器配置"""
        return {
            "input": [
                # Manus特有的输入框选择器
                'textarea[placeholder*="输入"]',
                'textarea[placeholder*="请输入"]',
                'textarea[placeholder*="问题"]',
                'textarea[placeholder*="研究"]',
                'textarea[placeholder*="分析"]',
                'textarea[placeholder*="content"]',
                'textarea[placeholder*="question"]',
                'div[contenteditable="true"][data-placeholder*="输入"]',
                'div[contenteditable="true"][placeholder*="输入"]',
                '.research-input textarea',
                '.question-input textarea',
                '.analysis-input textarea',
                '.prompt-input',
                '.manus-input',
                '.research-area',
                '.query-input',
                # 通用输入框
                'input[type="text"][placeholder*="输入"]',
                'textarea',
                'div[contenteditable="true"]',
                'input[type="text"]'
            ],
            "submit": [
                # Manus特有的提交按钮
                'button:has-text("开始研究")',
                'button:has-text("分析")',
                'button:has-text("研究")',
                'button:has-text("提交")',
                'button:has-text("发送")',
                'button:has-text("确定")',
                'button:has-text("开始")',
                'button:has-text("搜索")',
                'button:has-text("analyze")',
                'button:has-text("research")',
                'button:has-text("submit")',
                'button:has-text("start")',
                'button[aria-label*="提交"]',
                'button[aria-label*="开始"]',
                'button[aria-label*="研究"]',
                'button[data-action="submit"]',
                'button[data-action="research"]',
                'button[data-action="analyze"]',
                '.submit-button',
                '.research-button',
                '.analyze-button',
                '.start-button',
                '.query-button',
                # 通用提交按钮
                'button[type="submit"]',
                'input[type="submit"]'
            ],
            "loading": [
                # Manus特有的加载指示器
                '.loading',
                '.spinner',
                '.research-loading',
                '.analyzing',
                '.researching',
                '.processing',
                '.thinking',
                '.generating',
                '.working',
                '.manus-loading',
                '.progress-indicator',
                '[data-loading="true"]',
                '[data-status="analyzing"]',
                '[data-status="researching"]',
                '[data-status="processing"]',
                '[data-status="working"]',
                '[class*="loading"]',
                '[class*="spinner"]',
                '[class*="progress"]',
                '[class*="working"]'
            ],
            "content": [
                # Manus特有的内容选择器
                '.research-result',
                '.analysis-result',
                '.result',
                '.response',
                '.output',
                '.answer',
                '.content',
                '.generated-content',
                '.research-output',
                '.analysis-output',
                '.manus-result',
                '.report',
                '.summary',
                '.conclusion',
                '.findings',
                '.research-content',
                '.analysis-content',
                # 通用内容选择器
                '.message',
                '.text',
                'article',
                'main',
                '.main-content',
                '[role="main"]',
                '[data-content-type="result"]',
                '[data-content-type="analysis"]'
            ],
            "error": [
                # Manus特有的错误指示器
                '.error',
                '.failed',
                '.warning',
                '.alert',
                '.insufficient',
                '.limit-exceeded',
                '.quota-exceeded',
                '.analysis-failed',
                '.research-failed',
                '.manus-error',
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
        """获取Manus平台特定的关键词配置"""
        return {
            "title": [
                "manus",
                "研究",
                "分析",
                "智能分析",
                "research",
                "analysis",
                "ai research",
                "智能研究"
            ],
            "input_placeholder": [
                "输入",
                "请输入",
                "问题",
                "研究",
                "分析",
                "内容",
                "主题",
                "question",
                "research",
                "analysis"
            ],
            "submit_text": [
                "开始研究",
                "分析",
                "研究",
                "提交",
                "发送",
                "确定",
                "开始",
                "搜索",
                "analyze",
                "research",
                "submit",
                "start"
            ],
            "loading_indicators": [
                "正在研究",
                "分析中",
                "研究中",
                "处理中",
                "思考中",
                "生成中",
                "工作中",
                "analyzing",
                "researching",
                "processing",
                "working",
                "generating"
            ],
            "error_keywords": [
                "分析失败",
                "研究失败",
                "处理失败",
                "错误",
                "失败",
                "限制",
                "超限",
                "error",
                "failed",
                "limit",
                "exceeded"
            ]
        }
    
    def _get_platform_domains(self) -> List[str]:
        """获取Manus平台域名列表"""
        return [
            "manus.ai",
            "research.ai",
            "analysis.ai"
        ] 