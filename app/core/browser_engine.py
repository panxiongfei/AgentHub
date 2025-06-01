"""
增强版浏览器引擎
提供智能页面分析、元素定位、内容提取等高级功能
集成AI模型能力进行智能分析
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from playwright.async_api import Page, Locator

from app.core.logger import get_logger
from app.core.model_client import get_model_client, ModelResponse


@dataclass
class ElementInfo:
    """元素信息"""
    selector: str
    element_type: str
    text: str
    attributes: Dict[str, str]
    position: Dict[str, float]
    visible: bool
    confidence: float


@dataclass
class PageState:
    """页面状态"""
    url: str
    title: str
    content_hash: str
    load_state: str
    elements: List[ElementInfo] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class OperationResult:
    """操作结果"""
    success: bool
    operation_type: str
    target: str
    result: Any = None
    error: str = ""
    before_state: Optional[PageState] = None
    after_state: Optional[PageState] = None


class EnhancedBrowserEngine:
    """增强版浏览器引擎"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger("enhanced_browser_engine")
        
        # 操作历史
        self.operation_history: List[OperationResult] = []
        
        # 页面状态缓存
        self.page_states: List[PageState] = []
        
        # 选择器策略
        self.selector_strategies = {
            "input": [
                'input[type="text"]',
                'input[type="search"]', 
                'textarea',
                'div[contenteditable="true"]',
                '[placeholder]',
                '.input',
                '.search-input',
                '.text-input'
            ],
            "submit": [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("提交")',
                'button:has-text("发送")',
                'button:has-text("搜索")',
                'button:has-text("确定")',
                '.submit-button',
                '.send-button',
                '.search-button'
            ],
            "loading": [
                '.loading',
                '.spinner',
                '.progress',
                '[data-loading="true"]',
                '.dots-loading',
                '[class*="loading"]',
                '[class*="spinner"]'
            ],
            "content": [
                '.content',
                '.result',
                '.response',
                '.output',
                '.message',
                'main',
                'article',
                '.main-content',
                '[role="main"]'
            ],
            "error": [
                '.error',
                '.alert',
                '.warning',
                '[role="alert"]',
                '.error-message',
                '[class*="error"]',
                '[class*="alert"]'
            ]
        }
    
    async def capture_page_state(self) -> PageState:
        """捕获当前页面状态"""
        try:
            url = self.page.url
            title = await self.page.title()
            content = await self.page.content()
            content_hash = hashlib.md5(content.encode()).hexdigest()
            load_state = await self.page.evaluate("document.readyState")
            
            # 检测错误
            errors = await self._detect_page_errors()
            
            state = PageState(
                url=url,
                title=title,
                content_hash=content_hash,
                load_state=load_state,
                errors=errors
            )
            
            self.page_states.append(state)
            return state
            
        except Exception as e:
            self.logger.error(f"捕获页面状态失败: {e}")
            return PageState("", "", "", "unknown")
    
    async def _detect_page_errors(self) -> List[str]:
        """检测页面错误"""
        errors = []
        
        try:
            # 检查错误元素
            error_selectors = self.selector_strategies["error"]
            
            for selector in error_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            text = await element.text_content()
                            if text and text.strip():
                                errors.append(text.strip())
                except:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"错误检测失败: {e}")
        
        return errors
    
    async def analyze_page_intelligence(self) -> Dict[str, Any]:
        """智能分析页面"""
        try:
            # 捕获页面状态
            page_state = await self.capture_page_state()
            
            # 分析页面元素
            element_analysis = await self._analyze_page_elements()
            
            # 查找交互机会
            interaction_opportunities = await self._find_interaction_opportunities()
            
            # 评估内容就绪状态
            content_readiness = await self._assess_content_readiness()
            
            # 生成建议
            recommendations = await self._generate_recommendations(
                element_analysis, interaction_opportunities, content_readiness
            )
            
            analysis = {
                "page_info": {
                    "url": page_state.url,
                    "title": page_state.title,
                    "load_state": page_state.load_state,
                    "content_hash": page_state.content_hash
                },
                "element_analysis": element_analysis,
                "interaction_opportunities": interaction_opportunities,
                "content_readiness": content_readiness,
                "errors_detected": page_state.errors,
                "recommendations": recommendations
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"页面智能分析失败: {e}")
            return {"error": str(e)}
    
    async def _analyze_page_elements(self) -> Dict[str, Any]:
        """分析页面元素"""
        try:
            total_elements = await self.page.evaluate("document.querySelectorAll('*').length")
            
            element_types = {}
            
            for element_type, selectors in self.selector_strategies.items():
                count = 0
                for selector in selectors:
                    try:
                        elements = await self.page.locator(selector).all()
                        count += len(elements)
                    except:
                        continue
                element_types[element_type] = count
            
            return {
                "total_elements": total_elements,
                "by_type": element_types
            }
            
        except Exception as e:
            self.logger.error(f"元素分析失败: {e}")
            return {}
    
    async def _find_interaction_opportunities(self) -> List[Dict[str, Any]]:
        """查找交互机会"""
        opportunities = []
        
        try:
            for opp_type, selectors in self.selector_strategies.items():
                for selector in selectors:
                    try:
                        elements = await self.page.locator(selector).all()
                        for i, element in enumerate(elements):
                            if await element.is_visible():
                                # 计算置信度
                                confidence = await self._calculate_element_confidence(element, selector, opp_type)
                                
                                if confidence > 0.3:  # 只保留高置信度的机会
                                    text = await element.text_content() or ""
                                    
                                    opportunities.append({
                                        "type": opp_type,
                                        "selector": selector,
                                        "index": i,
                                        "text": text[:50],
                                        "confidence": confidence
                                    })
                    except:
                        continue
            
            # 按置信度排序
            opportunities.sort(key=lambda x: x["confidence"], reverse=True)
            
            return opportunities[:10]  # 返回前10个最佳机会
            
        except Exception as e:
            self.logger.error(f"查找交互机会失败: {e}")
            return []
    
    async def _calculate_element_confidence(self, element: Locator, selector: str, element_type: str) -> float:
        """计算元素置信度"""
        try:
            confidence = 0.0
            
            # 基础可见性权重
            if await element.is_visible():
                confidence += 0.3
            
            # 选择器特异性权重
            if "#" in selector:
                confidence += 0.3
            elif "." in selector:
                confidence += 0.2
            elif "[" in selector:
                confidence += 0.2
            else:
                confidence += 0.1
            
            # 文本相关性权重
            text = await element.text_content() or ""
            if text:
                if element_type == "submit" and any(word in text.lower() for word in ["提交", "发送", "搜索", "确定", "submit", "send"]):
                    confidence += 0.3
                elif element_type == "input" and any(word in text.lower() for word in ["输入", "搜索", "内容", "input", "search"]):
                    confidence += 0.2
            
            # 属性匹配权重
            try:
                attributes = await element.evaluate("el => Array.from(el.attributes).map(attr => ({name: attr.name, value: attr.value}))")
                for attr in attributes:
                    if element_type == "input" and attr["name"] in ["placeholder", "type"]:
                        confidence += 0.1
                    elif element_type == "submit" and attr["name"] in ["type", "role"]:
                        confidence += 0.1
            except:
                pass
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.warning(f"计算元素置信度失败: {e}")
            return 0.0
    
    async def _assess_content_readiness(self) -> bool:
        """评估内容就绪状态"""
        try:
            # 检查是否有加载指示器
            loading_selectors = self.selector_strategies["loading"]
            for selector in loading_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            return False  # 仍在加载中
                except:
                    continue
            
            # 检查内容区域
            content_selectors = self.selector_strategies["content"]
            content_found = False
            
            for selector in content_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            text = await element.text_content()
                            if text and len(text.strip()) > 50:  # 有实质性内容
                                content_found = True
                                break
                    if content_found:
                        break
                except:
                    continue
            
            return content_found
            
        except Exception as e:
            self.logger.error(f"评估内容就绪状态失败: {e}")
            return False
    
    async def _generate_recommendations(self, element_analysis: Dict, opportunities: List, content_ready: bool) -> List[str]:
        """生成智能建议"""
        recommendations = []
        
        try:
            if not content_ready:
                recommendations.append("页面内容尚未完全加载，建议等待")
            
            input_count = element_analysis.get("by_type", {}).get("input", 0)
            if input_count == 0:
                recommendations.append("未发现输入框，可能需要导航到正确页面")
            elif input_count > 1:
                recommendations.append(f"发现{input_count}个输入框，建议选择最合适的")
            
            submit_count = element_analysis.get("by_type", {}).get("submit", 0)
            if submit_count == 0:
                recommendations.append("未发现提交按钮，可能需要使用回车键提交")
            
            error_count = element_analysis.get("by_type", {}).get("error", 0)
            if error_count > 0:
                recommendations.append("检测到错误信息，建议检查页面状态")
            
            if len(opportunities) > 5:
                recommendations.append("发现多个交互机会，建议按置信度选择")
            elif len(opportunities) == 0:
                recommendations.append("未发现明显的交互机会，可能需要等待或刷新")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"生成建议失败: {e}")
            return []
    
    async def smart_input_text(self, text: str) -> OperationResult:
        """智能输入文本"""
        try:
            before_state = await self.capture_page_state()
            
            # 查找最佳输入框
            input_selectors = self.selector_strategies["input"]
            best_element = None
            best_confidence = 0
            
            for selector in input_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            confidence = await self._calculate_element_confidence(element, selector, "input")
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_element = element
                except:
                    continue
            
            if not best_element:
                result = OperationResult(
                    success=False,
                    operation_type="input",
                    target="text",
                    error="未找到可用的输入框",
                    before_state=before_state
                )
                self.operation_history.append(result)
                return result
            
            # 清空输入框并输入文本
            await best_element.clear()
            await best_element.fill(text)
            
            after_state = await self.capture_page_state()
            
            result = OperationResult(
                success=True,
                operation_type="input",
                target="text",
                result=text,
                before_state=before_state,
                after_state=after_state
            )
            
            self.operation_history.append(result)
            self.logger.info(f"成功输入文本: {text[:50]}...")
            
            return result
            
        except Exception as e:
            self.logger.error(f"智能输入文本失败: {e}")
            result = OperationResult(
                success=False,
                operation_type="input",
                target="text",
                error=str(e)
            )
            self.operation_history.append(result)
            return result
    
    async def smart_submit(self) -> OperationResult:
        """智能提交"""
        try:
            before_state = await self.capture_page_state()
            
            # 查找最佳提交按钮
            submit_selectors = self.selector_strategies["submit"]
            best_element = None
            best_confidence = 0
            
            for selector in submit_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            confidence = await self._calculate_element_confidence(element, selector, "submit")
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_element = element
                except:
                    continue
            
            if best_element:
                # 点击提交按钮
                await best_element.click()
                method = "button_click"
            else:
                # 尝试使用回车键提交
                await self.page.keyboard.press("Enter")
                method = "enter_key"
            
            # 等待页面响应
            await asyncio.sleep(2)
            
            after_state = await self.capture_page_state()
            
            result = OperationResult(
                success=True,
                operation_type="submit",
                target="form",
                result=method,
                before_state=before_state,
                after_state=after_state
            )
            
            self.operation_history.append(result)
            self.logger.info(f"成功提交表单: {method}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"智能提交失败: {e}")
            result = OperationResult(
                success=False,
                operation_type="submit",
                target="form",
                error=str(e)
            )
            self.operation_history.append(result)
            return result
    
    async def smart_wait_for_content(self, timeout: int = 60) -> OperationResult:
        """智能等待内容生成"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 检查内容就绪状态
                content_ready = await self._assess_content_readiness()
                
                if content_ready:
                    result = OperationResult(
                        success=True,
                        operation_type="wait",
                        target="content",
                        result="content_ready"
                    )
                    self.operation_history.append(result)
                    self.logger.info("内容已准备就绪")
                    return result
                
                # 检查错误状态
                errors = await self._detect_page_errors()
                if errors:
                    # 有错误但继续等待，可能是临时的
                    self.logger.warning(f"检测到错误: {errors}")
                
                await asyncio.sleep(3)  # 等待3秒后重新检查
            
            # 超时
            result = OperationResult(
                success=False,
                operation_type="wait",
                target="content",
                error=f"等待内容超时 ({timeout}秒)"
            )
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"智能等待内容失败: {e}")
            result = OperationResult(
                success=False,
                operation_type="wait",
                target="content",
                error=str(e)
            )
            self.operation_history.append(result)
            return result
    
    async def smart_extract_content(self) -> OperationResult:
        """智能提取内容"""
        try:
            content_selectors = self.selector_strategies["content"]
            extracted_contents = []
            
            for selector in content_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            text = await element.text_content()
                            if text and len(text.strip()) > 20:  # 过滤掉太短的内容
                                extracted_contents.append({
                                    "selector": selector,
                                    "text": text.strip(),
                                    "length": len(text.strip())
                                })
                except:
                    continue
            
            if not extracted_contents:
                # 尝试提取整个页面的文本内容
                try:
                    body_text = await self.page.locator("body").text_content()
                    if body_text and len(body_text.strip()) > 50:
                        extracted_contents.append({
                            "selector": "body",
                            "text": body_text.strip(),
                            "length": len(body_text.strip())
                        })
                except:
                    pass
            
            if extracted_contents:
                # 选择最长的内容作为主要结果
                best_content = max(extracted_contents, key=lambda x: x["length"])
                
                result = OperationResult(
                    success=True,
                    operation_type="extract",
                    target="content",
                    result=best_content["text"]
                )
                
                self.operation_history.append(result)
                self.logger.info(f"成功提取内容，长度: {best_content['length']}")
                
                return result
            else:
                result = OperationResult(
                    success=False,
                    operation_type="extract",
                    target="content",
                    error="未找到可提取的内容"
                )
                self.operation_history.append(result)
                return result
            
        except Exception as e:
            self.logger.error(f"智能提取内容失败: {e}")
            result = OperationResult(
                success=False,
                operation_type="extract",
                target="content",
                error=str(e)
            )
            self.operation_history.append(result)
            return result
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """获取操作历史摘要"""
        try:
            total_ops = len(self.operation_history)
            successful_ops = len([op for op in self.operation_history if op.success])
            
            operation_types = {}
            for op in self.operation_history:
                op_type = op.operation_type
                if op_type not in operation_types:
                    operation_types[op_type] = {"total": 0, "successful": 0}
                operation_types[op_type]["total"] += 1
                if op.success:
                    operation_types[op_type]["successful"] += 1
            
            return {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "success_rate": successful_ops / total_ops if total_ops > 0 else 0,
                "operation_types": operation_types,
                "page_states_captured": len(self.page_states)
            }
            
        except Exception as e:
            self.logger.error(f"获取操作摘要失败: {e}")
            return {}
    
    async def ai_analyze_page_structure(self, include_screenshot: bool = True) -> Dict[str, Any]:
        """使用AI分析页面结构"""
        try:
            self.logger.info("开始AI页面结构分析...")
            
            # 获取页面基本信息
            url = self.page.url
            title = await self.page.title()
            
            # 获取页面的DOM结构摘要
            dom_summary = await self._extract_dom_summary()
            
            # 构建分析提示
            prompt = f"""
            请分析这个网页的结构和功能，这是一个{url}页面。
            
            页面信息：
            - 标题：{title}
            - URL：{url}
            - DOM元素摘要：{dom_summary}
            
            请识别：
            1. 页面的主要功能和目的
            2. 关键的交互元素（输入框、按钮、链接等）
            3. 内容区域的布局
            4. 可能的用户操作流程
            5. 页面是否完全加载完成
            
            请用JSON格式返回分析结果：
            {{
                "page_purpose": "页面的主要目的",
                "key_elements": ["关键元素1", "关键元素2"],
                "interaction_flow": ["操作步骤1", "操作步骤2"],
                "loading_status": "complete/loading/error",
                "recommendations": ["建议1", "建议2"]
            }}
            """
            
            # 如果需要截图分析
            ai_response = None
            if include_screenshot:
                screenshot_path = await self._take_temp_screenshot()
                if screenshot_path:
                    model_client = get_model_client()
                    ai_response = await model_client.analyze_image(
                        screenshot_path,
                        prompt,
                        max_tokens=1000
                    )
                    # 清理临时文件
                    screenshot_path.unlink(missing_ok=True)
            
            # 如果没有截图或截图分析失败，使用文本分析
            if not ai_response:
                model_client = get_model_client()
                ai_response = await model_client.chat_completion([
                    {"role": "user", "content": prompt}
                ], max_tokens=1000)
            
            # 解析AI响应
            try:
                import json
                import re
                
                # 尝试从响应中提取JSON
                response_text = ai_response.content.strip()
                
                # 尝试直接解析
                try:
                    ai_analysis = json.loads(response_text)
                except json.JSONDecodeError:
                    # 尝试提取JSON块
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        ai_analysis = json.loads(json_match.group())
                    else:
                        raise ValueError("无法找到JSON格式的响应")
                        
            except Exception as e:
                self.logger.warning(f"解析AI响应失败: {e}")
                # 创建基于文本分析的基础结果
                ai_analysis = {
                    "page_purpose": self._extract_purpose_from_text(ai_response.content),
                    "key_elements": self._extract_elements_from_text(ai_response.content),
                    "interaction_flow": self._extract_flow_from_text(ai_response.content),
                    "loading_status": "unknown",
                    "recommendations": self._extract_recommendations_from_text(ai_response.content),
                    "raw_response": ai_response.content[:500]  # 保留原始响应的一部分
                }
            
            # 组合分析结果
            enhanced_analysis = {
                "basic_analysis": await self.analyze_page_intelligence(),
                "ai_analysis": ai_analysis,
                "ai_model_info": {
                    "model": ai_response.model,
                    "provider": ai_response.provider,
                    "usage": ai_response.usage
                },
                "timestamp": time.time()
            }
            
            self.logger.info("AI页面结构分析完成")
            return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"AI页面结构分析失败: {e}")
            return {"error": str(e)}
    
    async def ai_find_best_elements(self, target_type: str, context: str = "") -> List[Dict[str, Any]]:
        """使用AI找到最佳的页面元素"""
        try:
            self.logger.info(f"使用AI查找最佳元素: {target_type}")
            
            # 获取页面截图
            screenshot_path = await self._take_temp_screenshot()
            if not screenshot_path:
                return []
            
            # 构建AI提示
            prompt = f"""
            请分析这个网页截图，找到最适合{target_type}操作的元素。
            
            任务上下文：{context}
            
            请识别：
            1. 最可能用于{target_type}的元素位置
            2. 元素的特征描述
            3. 推荐的操作方式
            4. 置信度评分(0-1)
            
            返回JSON格式：
            {{
                "elements": [
                    {{
                        "description": "元素描述",
                        "location": "大致位置描述",
                        "confidence": 0.9,
                        "operation": "推荐操作"
                    }}
                ]
            }}
            """
            
            # 使用AI分析
            model_client = get_model_client()
            ai_response = await model_client.analyze_image(
                screenshot_path, 
                prompt,
                max_tokens=800
            )
            
            # 清理临时文件
            screenshot_path.unlink(missing_ok=True)
            
            # 解析响应
            try:
                import json
                import re
                
                response_text = ai_response.content.strip()
                
                # 尝试直接解析
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    # 尝试提取JSON块
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        # 如果无法解析JSON，创建基础响应
                        result = {"elements": self._extract_elements_from_ai_text(response_text, target_type)}
                
                elements = result.get("elements", [])
                
                self.logger.info(f"AI找到 {len(elements)} 个候选元素")
                return elements
                
            except Exception as e:
                self.logger.warning(f"解析AI响应失败: {e}")
                # 返回基于文本分析的基础元素
                return self._extract_elements_from_ai_text(ai_response.content, target_type)
            
        except Exception as e:
            self.logger.error(f"AI元素查找失败: {e}")
            return []
    
    async def ai_extract_and_summarize_content(self) -> Dict[str, Any]:
        """使用AI提取并总结页面内容"""
        try:
            self.logger.info("开始AI内容提取和总结...")
            
            # 首先使用传统方法提取内容
            extract_result = await self.smart_extract_content()
            
            if not extract_result.success:
                return {"error": "无法提取页面内容"}
            
            content = extract_result.result
            
            # 使用AI进行总结
            model_client = get_model_client()
            
            # 清理内容，移除CSS和脚本等噪音
            cleaned_content = self._clean_content_for_ai(content)
            
            summary_response = await model_client.summarize_text(
                cleaned_content[:6000],  # 限制长度
                "请对以下网页内容进行智能分析和总结，重点关注主要信息和关键内容："
            )
            
            # 获取页面截图用于视觉分析
            screenshot_path = await self._take_temp_screenshot()
            visual_analysis = None
            
            if screenshot_path:
                visual_prompt = "请描述这个网页的视觉布局、主要元素和整体设计风格。重点关注内容的组织方式和用户界面特点。"
                
                visual_response = await model_client.analyze_image(
                    screenshot_path,
                    visual_prompt,
                    max_tokens=500
                )
                
                visual_analysis = visual_response.content
                screenshot_path.unlink(missing_ok=True)
            
            # 组合结果
            result = {
                "original_content": content,
                "content_length": len(content),
                "ai_summary": summary_response.content,
                "visual_analysis": visual_analysis,
                "extraction_method": "smart_engine_with_ai",
                "ai_model_info": {
                    "model": summary_response.model,
                    "provider": summary_response.provider,
                    "usage": summary_response.usage
                },
                "timestamp": time.time()
            }
            
            self.logger.info("AI内容提取和总结完成")
            return result
            
        except Exception as e:
            self.logger.error(f"AI内容提取和总结失败: {e}")
            return {"error": str(e)}
    
    async def ai_generate_operation_strategy(self, task_goal: str) -> Dict[str, Any]:
        """使用AI生成操作策略"""
        try:
            self.logger.info(f"生成操作策略: {task_goal}")
            
            # 获取当前页面分析
            page_analysis = await self.analyze_page_intelligence()
            
            # 获取页面截图
            screenshot_path = await self._take_temp_screenshot()
            if not screenshot_path:
                return {"error": "无法获取页面截图"}
            
            # 构建策略生成提示
            strategy_prompt = f"""
            基于这个网页截图和页面分析，为以下任务目标制定操作策略：
            
            任务目标：{task_goal}
            
            页面信息：
            - URL: {page_analysis['page_info']['url']}
            - 标题: {page_analysis['page_info']['title']}
            - 加载状态: {page_analysis['page_info']['load_state']}
            - 内容就绪: {page_analysis['content_readiness']}
            - 发现的交互机会: {len(page_analysis['interaction_opportunities'])}
            
            请制定详细的操作策略，包括：
            1. 操作步骤序列
            2. 每个步骤的具体动作
            3. 预期结果和验证方法
            4. 可能的风险和备选方案
            5. 成功指标
            
            返回JSON格式：
            {{
                "strategy": {{
                    "steps": [
                        {{
                            "step": 1,
                            "action": "具体动作",
                            "target": "目标元素",
                            "expected_result": "预期结果",
                            "verification": "验证方法"
                        }}
                    ],
                    "risks": ["风险1", "风险2"],
                    "alternatives": ["备选方案1"],
                    "success_criteria": ["成功指标1"]
                }}
            }}
            """
            
            # 使用AI生成策略
            model_client = get_model_client()
            strategy_response = await model_client.analyze_image(
                screenshot_path,
                strategy_prompt,
                max_tokens=1500
            )
            
            # 清理临时文件
            screenshot_path.unlink(missing_ok=True)
            
            # 解析策略
            try:
                import json
                strategy = json.loads(strategy_response.content)
                
                result = {
                    "task_goal": task_goal,
                    "strategy": strategy,
                    "page_context": page_analysis,
                    "ai_model_info": {
                        "model": strategy_response.model,
                        "provider": strategy_response.provider,
                        "usage": strategy_response.usage
                    },
                    "timestamp": time.time()
                }
                
                self.logger.info("操作策略生成完成")
                return result
                
            except Exception as e:
                self.logger.warning(f"解析策略响应失败: {e}")
                return {
                    "task_goal": task_goal,
                    "strategy": {"raw_response": strategy_response.content},
                    "error": "策略解析失败"
                }
            
        except Exception as e:
            self.logger.error(f"生成操作策略失败: {e}")
            return {"error": str(e)}
    
    async def _extract_dom_summary(self) -> str:
        """提取DOM结构摘要"""
        try:
            # 获取页面的关键DOM信息
            dom_info = await self.page.evaluate("""
                () => {
                    const summary = {
                        total_elements: document.querySelectorAll('*').length,
                        inputs: document.querySelectorAll('input, textarea').length,
                        buttons: document.querySelectorAll('button, input[type="submit"]').length,
                        links: document.querySelectorAll('a').length,
                        forms: document.querySelectorAll('form').length,
                        images: document.querySelectorAll('img').length,
                        headings: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
                        main_text_length: document.body ? document.body.innerText.length : 0
                    };
                    return summary;
                }
            """)
            
            summary = f"页面包含{dom_info['total_elements']}个元素，{dom_info['inputs']}个输入框，{dom_info['buttons']}个按钮，{dom_info['links']}个链接，{dom_info['forms']}个表单，文本内容长度{dom_info['main_text_length']}"
            
            return summary
            
        except Exception as e:
            self.logger.warning(f"提取DOM摘要失败: {e}")
            return "DOM信息获取失败"
    
    async def _take_temp_screenshot(self) -> Optional[Path]:
        """拍摄临时截图"""
        try:
            temp_dir = Path("data/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = temp_dir / f"ai_analysis_{int(time.time())}.png"
            
            await self.page.screenshot(path=str(screenshot_path), full_page=False)
            
            return screenshot_path
            
        except Exception as e:
            self.logger.warning(f"拍摄截图失败: {e}")
            return None
    
    def _extract_purpose_from_text(self, text: str) -> str:
        """从文本中提取页面目的"""
        try:
            import re
            # 查找目的相关的描述
            purpose_patterns = [
                r"页面.*?是.*?用于([^。]+)",
                r"主要.*?功能.*?是([^。]+)",
                r"这个.*?页面.*?用于([^。]+)",
                r"目的.*?是([^。]+)"
            ]
            
            for pattern in purpose_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
            
            # 如果没有找到特定模式，返回前100个字符
            return text[:100].replace('\n', ' ').strip()
            
        except Exception:
            return "AI分析页面目的"
    
    def _extract_elements_from_text(self, text: str) -> List[str]:
        """从文本中提取关键元素"""
        try:
            import re
            elements = []
            
            # 查找提到的UI元素
            element_patterns = [
                r"(输入框|文本框|搜索框)",
                r"(按钮|提交|确定|发送)",
                r"(链接|导航|菜单)",
                r"(表单|表格|列表)",
                r"(图片|图像|截图)",
                r"(标题|标签|文本)"
            ]
            
            for pattern in element_patterns:
                matches = re.findall(pattern, text)
                elements.extend(matches)
            
            return list(set(elements))  # 去重
            
        except Exception:
            return ["输入框", "按钮", "文本"]
    
    def _extract_flow_from_text(self, text: str) -> List[str]:
        """从文本中提取交互流程"""
        try:
            import re
            flow = []
            
            # 查找步骤相关的描述
            step_patterns = [
                r"(\d+[\.\、].*?)(?=\d+[\.\、]|$)",
                r"(首先.*?)(?=其次|然后|接下来|$)",
                r"(然后.*?)(?=接下来|最后|$)",
                r"(最后.*?)(?=\n|$)"
            ]
            
            for pattern in step_patterns:
                matches = re.findall(pattern, text, re.DOTALL)
                for match in matches:
                    cleaned = match.strip().replace('\n', ' ')
                    if len(cleaned) > 5:
                        flow.append(cleaned)
            
            if not flow:
                return ["输入内容", "点击提交", "等待结果"]
            
            return flow[:5]  # 最多返回5个步骤
            
        except Exception:
            return ["输入内容", "提交表单"]
    
    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """从文本中提取建议"""
        try:
            import re
            recommendations = []
            
            # 查找建议相关的描述
            rec_patterns = [
                r"建议([^。]+)",
                r"推荐([^。]+)",
                r"应该([^。]+)",
                r"需要([^。]+)"
            ]
            
            for pattern in rec_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    cleaned = match.strip()
                    if len(cleaned) > 3:
                        recommendations.append(cleaned)
            
            if not recommendations:
                return ["等待页面完全加载", "使用智能选择器定位元素"]
            
            return recommendations[:3]  # 最多返回3个建议
            
        except Exception:
            return ["使用智能分析"]
    
    def _extract_elements_from_ai_text(self, text: str, target_type: str) -> List[Dict[str, Any]]:
        """从AI文本响应中提取元素信息"""
        try:
            import re
            elements = []
            
            # 基于目标类型创建基础元素
            if "输入" in target_type or "input" in target_type.lower():
                elements.append({
                    "description": "页面输入框",
                    "location": "页面中央或顶部区域",
                    "confidence": 0.6,
                    "operation": "点击后输入文本"
                })
            elif "按钮" in target_type or "button" in target_type.lower():
                elements.append({
                    "description": "提交按钮",
                    "location": "表单底部或右侧",
                    "confidence": 0.6,
                    "operation": "点击提交"
                })
            
            # 尝试从文本中提取更多信息
            lines = text.split('\n')
            for line in lines:
                if any(word in line for word in ["输入框", "文本框", "搜索", "按钮", "链接"]):
                    # 提取这一行作为描述
                    if len(line.strip()) > 5:
                        elements.append({
                            "description": line.strip()[:100],
                            "location": "根据AI分析确定",
                            "confidence": 0.5,
                            "operation": f"用于{target_type}操作"
                        })
            
            return elements[:5]  # 最多返回5个元素
            
        except Exception:
            return [{
                "description": f"AI识别的{target_type}元素",
                "location": "页面中",
                "confidence": 0.4,
                "operation": f"执行{target_type}操作"
            }]
    
    def _clean_content_for_ai(self, content: str) -> str:
        """清理内容用于AI分析"""
        try:
            import re
            
            # 移除CSS样式
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<link[^>]*>', '', content, flags=re.IGNORECASE)
            
            # 移除JavaScript
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # 移除HTML注释
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            # 移除HTML标签但保留文本
            content = re.sub(r'<[^>]+>', ' ', content)
            
            # 移除多余的空白字符
            content = re.sub(r'\s+', ' ', content)
            
            # 移除CSS相关的行
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # 跳过CSS属性行
                if ':' in line and any(css_prop in line for css_prop in [
                    'color', 'background', 'font', 'margin', 'padding', 'border', 
                    'width', 'height', 'display', 'position', 'flex', 'grid'
                ]):
                    continue
                # 跳过纯符号行
                if len(line) > 0 and all(c in '{}();,.-_' for c in line):
                    continue
                # 保留有意义的文本
                if len(line) > 3 and any(c.isalnum() for c in line):
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines[:200])  # 限制行数
            
        except Exception as e:
            self.logger.warning(f"内容清理失败: {e}")
            # 简单清理：只移除明显的HTML标签
            try:
                import re
                cleaned = re.sub(r'<[^>]+>', ' ', content)
                cleaned = re.sub(r'\s+', ' ', cleaned)
                return cleaned[:3000]
            except:
                return content[:3000] 