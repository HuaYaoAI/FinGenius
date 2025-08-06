"""
HTML generation tool - Uses LLM to generate complete web pages
based on user requirements including styling and JavaScript interactions.
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from src.logger import logger
from src.prompt.create_html import CREATE_HTML_TEMPLATE_PROMPT, CREATE_HTML_TOOL_PROMPT


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.llm import LLM
from src.tool.base import BaseTool, ToolResult
from src.utils.report_manager import report_manager

"""
数据缓存与实时更新策略
"""
import json
import time
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

class DataCacheManager:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        
        # 缓存配置
        self.cache_config = {
            "chip_analysis": {"ttl": 300, "max_age": 900},      # 5分钟TTL，15分钟最大age
            "stock_info": {"ttl": 60, "max_age": 180},           # 1分钟TTL，3分钟最大age
            "sentiment_data": {"ttl": 600, "max_age": 1800},     # 10分钟TTL，30分钟最大age
            "technical_analysis": {"ttl": 180, "max_age": 600},  # 3分钟TTL，10分钟最大age
            "risk_control": {"ttl": 120, "max_age": 360},        # 2分钟TTL，6分钟最大age
        }
    
    def ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_key(self, data_type: str, stock_code: str, **kwargs) -> str:
        """生成缓存键"""
        params = "_".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return f"{data_type}_{stock_code}_{params}" if params else f"{data_type}_{stock_code}"
    
    def get_cache_file(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get_cached_data(self, data_type: str, stock_code: str, **kwargs) -> Optional[Dict]:
        """获取缓存数据"""
        try:
            cache_key = self.get_cache_key(data_type, stock_code, **kwargs)
            cache_file = self.get_cache_file(cache_key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # 检查缓存是否过期
            cache_time = cached_data.get('cache_time', 0)
            current_time = time.time()
            
            config = self.cache_config.get(data_type, {"ttl": 300, "max_age": 900})
            
            # 硬过期检查
            if current_time - cache_time > config['max_age']:
                self.remove_cache(cache_key)
                return None
            
            # 软过期检查 - 返回但标记为过期
            if current_time - cache_time > config['ttl']:
                cached_data['is_stale'] = True
            else:
                cached_data['is_stale'] = False
            
            return cached_data
            
        except Exception as e:
            print(f"获取缓存数据失败: {str(e)}")
            return None
    
    def set_cached_data(self, data_type: str, stock_code: str, data: Any, **kwargs):
        """设置缓存数据"""
        try:
            cache_key = self.get_cache_key(data_type, stock_code, **kwargs)
            cache_file = self.get_cache_file(cache_key)
            
            cache_data = {
                "cache_time": time.time(),
                "data_type": data_type,
                "stock_code": stock_code,
                "data": data,
                "metadata": kwargs
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"设置缓存数据失败: {str(e)}")
    
    def remove_cache(self, cache_key: str):
        """删除缓存"""
        try:
            cache_file = self.get_cache_file(cache_key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        except Exception as e:
            print(f"删除缓存失败: {str(e)}")
    
    def cleanup_expired_cache(self):
        """清理过期缓存"""
        try:
            current_time = time.time()
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cached_data = json.load(f)
                        
                        cache_time = cached_data.get('cache_time', 0)
                        data_type = cached_data.get('data_type', 'unknown')
                        
                        config = self.cache_config.get(data_type, {"ttl": 300, "max_age": 900})
                        
                        if current_time - cache_time > config['max_age']:
                            os.remove(file_path)
                            
                    except Exception:
                        # 如果文件损坏，删除它
                        os.remove(file_path)
                        
        except Exception as e:
            print(f"清理过期缓存失败: {str(e)}")

# 全局缓存管理器实例
cache_manager = DataCacheManager()

def with_cache(data_type: str):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(self, stock_code: str, **kwargs):
            # 尝试从缓存获取数据
            cached_data = cache_manager.get_cached_data(data_type, stock_code, **kwargs)
            
            if cached_data and not cached_data.get('is_stale', False):
                print(f"使用缓存数据: {data_type}_{stock_code}")
                return cached_data['data']
            
            # 执行原始函数
            try:
                result = await func(self, stock_code, **kwargs)
                
                # 缓存结果
                if result:
                    cache_manager.set_cached_data(data_type, stock_code, result, **kwargs)
                
                return result
                
            except Exception as e:
                # 如果有过期但可用的缓存，返回缓存数据
                if cached_data and cached_data.get('is_stale', False):
                    print(f"使用过期缓存数据作为fallback: {data_type}_{stock_code}")
                    return cached_data['data']
                
                raise e
        
        return wrapper
    return decorator


class CreateHtmlTool(BaseTool):
    """HTML generation tool that creates beautiful and functional HTML pages
    with complex layouts, styling, and interactive features based on user requirements.
    """

    name: str = "create_html"
    description: str = (
        "创建美观、功能齐全的HTML页面，支持复杂的布局设计、样式和交互效果。可以根据需求生成各种类型的网页，如数据展示、报表、产品页等。"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "request": {
                "type": "string",
                "description": "详细描述需要生成的HTML页面需求",
            },
            "data": {
                "type": "object",
                "description": "需要在页面中展示的数据，JSON格式",
                "default": None,
            },
            "output_path": {
                "type": "string",
                "description": "输出HTML文件的路径 /to/path/file.html",
                "default": "",
            },
            "reference": {
                "type": "string",
                "description": "参考设计或布局说明",
                "default": "",
            },
            "additional_requirements": {
                "type": "string",
                "description": "其他额外要求",
                "default": "",
            },
        },
        "required": ["request", "output_path"],
    }

    # LLM instance for generating HTML
    llm: LLM = Field(default_factory=LLM)

    async def _generate_html(
        self, request: str, additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a complete HTML page based on user request"""
        logger.info(f"Starting HTML page generation: {request[:100]}...")

        # Build the complete prompt
        prompt = f"""请根据以下需求和HTML模板生成一个完整的HTML页面：

# 需求
{request}

# HTML模板
{CREATE_HTML_TEMPLATE_PROMPT}

# 重要要求
请确保在HTML页面的footer区域包含AI生成报告的免责声明，说明本报告由人工智能系统自动生成，仅供参考，不构成投资建议。
"""
        # Add additional context if provided
        if additional_context:
            if data := additional_context.get("data"):
                prompt += f"\n\nData to display:\n{json.dumps(data, ensure_ascii=False, indent=2)}"

            if reference := additional_context.get("reference"):
                prompt += f"\n\nReference design or layout:\n{reference}"

            if requirements := additional_context.get("requirements"):
                prompt += f"\n\nAdditional requirements:\n{requirements}"

        # Generate HTML using LLM
        messages = [
            {"role": "system", "content": CREATE_HTML_TOOL_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm.ask(messages=messages)
            html_code = self._extract_html_code(response)
            logger.info(
                f"HTML generation completed, length: {len(html_code)} characters"
            )
            return html_code
        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            raise

    def _extract_html_code(self, response: str) -> str:
        """Extract HTML code from LLM response with enhanced parsing"""
        logger.info(f"Extracting HTML from response, length: {len(response)}")
        
        # Method 1: Check for HTML code block with various formats
        html_block_patterns = [
            r"```html\s*\n(.*?)\n```",
            r"```HTML\s*\n(.*?)\n```", 
            r"```\s*html\s*\n(.*?)\n```",
            r"```\s*\n(<!DOCTYPE.*?)\n```",
        ]
        
        for pattern in html_block_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                html_content = match.group(1).strip()
                logger.info(f"Found HTML in code block using pattern: {pattern[:20]}...")
                return self._fix_encoding(html_content)
        
        # Method 2: Look for direct HTML content
        html_start_patterns = [
            r"(<!DOCTYPE\s+html.*)",
            r"(<html[^>]*>.*)",
            r"(<!doctype\s+html.*)"
        ]
        
        for pattern in html_start_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                html_content = match.group(1).strip()
                logger.info(f"Found direct HTML using pattern: {pattern[:20]}...")
                return self._fix_encoding(html_content)
        
        # Method 3: Fallback - look for any HTML-like content
        if "<html" in response.lower() or "<!doctype" in response.lower():
            # Find the start position
            start_markers = ["<!DOCTYPE", "<!doctype", "<html", "<HTML"]
            start_pos = -1
            for marker in start_markers:
                pos = response.find(marker)
                if pos != -1:
                    start_pos = pos
                    break
            
            if start_pos != -1:
                html_content = response[start_pos:].strip()
                logger.info(f"Found HTML using fallback method at position {start_pos}")
                return self._fix_encoding(html_content)
        
        # Method 4: Last resort - return full response
        logger.warning("No clear HTML structure found, returning full response")
        return self._fix_encoding(response)
    
    def _sanitize_data_for_js(self, data: Any) -> Any:
        """Recursively sanitize data to prevent JavaScript injection issues"""
        if isinstance(data, dict):
            return {k: self._sanitize_data_for_js(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data_for_js(item) for item in data]
        elif isinstance(data, str):
            # Only truncate extremely long strings, let json.dumps handle escaping
            if len(data) > 20000:  # 增加长度限制，避免过度截断
                return data[:19977] + "..."
            return data
        else:
            return data
    
    def _inject_data_into_html(self, html_content: str, data: Dict[str, Any]) -> str:
        """Inject data into HTML template with enhanced robustness and validation"""
        try:
            import json
            logger.info("Starting data injection into HTML...")
            
            # Sanitize data first to prevent injection issues
            sanitized_data = self._sanitize_data_for_js(data)
            logger.info(f"Data sanitized, keys: {list(sanitized_data.keys()) if isinstance(sanitized_data, dict) else 'non-dict'}")
            
            # Properly serialize data with safe escaping for JavaScript injection
            safe_data = json.dumps(
                sanitized_data, 
                ensure_ascii=True,  # 确保非ASCII字符被转义
                indent=2, 
                separators=(',', ': '),
                sort_keys=True  # 排序键值
            )
            logger.info(f"Data serialized to JSON, length: {len(safe_data)}")
            
            injection_success = False
            
            # 更健壮的现有数据检测
            existing_patterns = [
                r'\b(?:let|const|var)\s+reportData\s*=',
                r'window\.(?:pageData|reportData)\s*='
            ]
            
            existing_matches = []
            for pattern in existing_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                existing_matches.extend(matches)
            
            has_existing_data = len(existing_matches) > 0
            logger.info(f"Existing data declarations found: {len(existing_matches)} - {existing_matches}")
            
            if has_existing_data:
                logger.info("Attempting to replace existing data declarations...")
                
                # 更精确的替换模式，支持多行和复杂对象
                replacement_patterns = [
                    # 匹配 const/let/var reportData = { ... }; 格式
                    (r'(\b(?:const|let|var)\s+reportData\s*=\s*)\{[\s\S]*?\}(\s*;?)', f'\\1{safe_data}\\2'),
                    # 匹配 window.pageData = { ... }; 格式
                    (r'(window\.(?:pageData|reportData)\s*=\s*)\{[\s\S]*?\}(\s*;?)', f'\\1{safe_data}\\2'),
                    # 匹配注释格式的占位符
                    (r'(\b(?:const|let|var)\s+reportData\s*=\s*)\{\}(\s*;?\s*//[^\n]*)', f'\\1{safe_data}\\2'),
                ]
                
                for i, (pattern, replacement) in enumerate(replacement_patterns):
                    matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                    if matches:
                        logger.info(f"Pattern {i+1} matched {len(matches)} times: {pattern[:50]}...")
                        html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL | re.IGNORECASE)
                        # 注入数据加载完成标记
                        html_content = html_content.replace('window.dataLoadingState = {', 'window.dataLoadingState = {')
                        html_content = re.sub(
                            r'(window\.dataLoadingState\s*=\s*\{[^}]*\})',
                            '\1;\n        window.dataLoadingState.isLoaded = true;',
                            html_content,
                            count=1
                        )
                        logger.info(f"Successfully replaced existing data using pattern {i+1}")
                        injection_success = True
                        break
                
            else:
                logger.info("No existing data found, attempting fresh injection...")
                
                # 更全面的注入点查找
                injection_patterns = [
                    # 空对象占位符
                    (r'\b(const|let|var)\s+reportData\s*=\s*\{\}\s*;', f'\\1 reportData = {safe_data};'),
                    (r'window\.(pageData|reportData)\s*=\s*\{\}\s*;', f'window.\\1 = {safe_data};'),
                    # 带注释的占位符
                    (r'(\b(?:const|let|var)\s+reportData\s*=\s*)\{\}(\s*;?\s*//[^\n]*)', f'\\1{safe_data}\\2'),
                    # 模板中的特殊注释
                    (r'//\s*页面数据注入点[^\n]*\n', f'// 页面数据注入点\n        const reportData = {safe_data};\n'),
                ]
                
                for i, (pattern, replacement) in enumerate(injection_patterns):
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        logger.info(f"Injection pattern {i+1} matched {len(matches)} times: {pattern[:50]}...")
                        html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.IGNORECASE)
                        logger.info(f"Successfully injected data using pattern {i+1}")
                        injection_success = True
                        break
            
            # 增强的fallback机制
            if not injection_success:
                logger.warning("Standard injection failed, attempting enhanced fallback...")
                
                # 查找所有可能的script标签
                script_patterns = [
                    r'<script[^>]*>\s*',  # 任何script标签开始
                    r'<script>\s*',       # 简单script标签
                ]
                
                for pattern in script_patterns:
                    match = re.search(pattern, html_content, re.IGNORECASE)
                    if match:
                        insertion_point = match.end()
                        data_injection = f"\n        // 页面数据全局变量 - 自动注入\n        const reportData = {safe_data};\n        // 设置数据加载状态\n        window.dataLoadingState.isLoaded = true;\n"
                        html_content = html_content[:insertion_point] + data_injection + html_content[insertion_point:]
                        logger.info(f"Successfully injected data using fallback at position {insertion_point}")
                        injection_success = True
                        break
            
            # 最终验证
            if injection_success:
                # 检查重复声明
                reportdata_declarations = re.findall(r'\b(?:let|const|var)\s+reportData\s*=', html_content, re.IGNORECASE)
                window_declarations = re.findall(r'window\.(?:pageData|reportData)\s*=', html_content, re.IGNORECASE)
                
                total_declarations = len(reportdata_declarations) + len(window_declarations)
                
                if total_declarations > 1:
                    logger.error(f"⚠️ Multiple data declarations detected: {total_declarations} (reportData: {len(reportdata_declarations)}, window: {len(window_declarations)})")
                    # 尝试清理重复声明
                    html_content = self._cleanup_duplicate_declarations(html_content)
                else:
                    logger.info(f"✅ Data injection successful, total declarations: {total_declarations}")
                
                # 验证JSON格式和数据结构
                try:
                    data_obj = json.loads(safe_data)
                    # 验证必需字段
                    required_fields = ['stock_code', 'battle_results', 'analysis_results', 'debate_results']
                    missing_fields = [field for field in required_fields if field not in data_obj]
                    
                    if missing_fields:
                        logger.error(f"❌ Missing required fields in data: {missing_fields}")
                    else:
                        # 验证数据类型
                        if not isinstance(data_obj.get('battle_results'), list):
                            logger.error("❌ battle_results must be an array")
                        if not isinstance(data_obj.get('debate_results'), list):
                            logger.error("❌ debate_results must be an array")
                        logger.info("✅ Injected data structure is valid")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Injected data is invalid JSON: {e}")
                    
            else:
                logger.error("❌ All injection methods failed")
                
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to inject data into HTML: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return html_content

    def _fix_encoding(self, html_content: str) -> str:
        """Fix potential encoding issues in HTML content with enhanced validation"""
        try:
            logger.info("Starting HTML encoding fix...")
            
            # Check if charset already exists and is correct
            charset_pattern = r'<meta\s+charset\s*=\s*["\']?([^"\'>\s]+)["\']?[^>]*>'
            charset_matches = re.findall(charset_pattern, html_content, re.IGNORECASE)
            
            if charset_matches:
                logger.info(f"Found existing charset declarations: {charset_matches}")
                # Remove all existing charset declarations first
                html_content = re.sub(
                    r'<meta\s+charset\s*=\s*["\']?[^"\'>\s]+["\']?[^>]*>',
                    '',
                    html_content,
                    flags=re.IGNORECASE
                )
                logger.info("Removed existing charset declarations")
            
            # Add single UTF-8 charset declaration after <head>
            head_pattern = r'(<head[^>]*>)'
            if re.search(head_pattern, html_content, re.IGNORECASE):
                html_content = re.sub(
                    head_pattern,
                    r'\1\n    <meta charset="UTF-8">',
                    html_content,
                    count=1,  # Only replace the first occurrence
                    flags=re.IGNORECASE
                )
                logger.info("Added UTF-8 charset declaration after <head>")
            else:
                logger.warning("No <head> tag found, cannot add charset declaration")
            
            # Validate the result
            final_charset_count = len(re.findall(charset_pattern, html_content, re.IGNORECASE))
            logger.info(f"Final charset declaration count: {final_charset_count}")
            
            if final_charset_count > 1:
                logger.warning(f"Multiple charset declarations detected: {final_charset_count}")
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error fixing HTML encoding: {e}")
            return html_content

    def _cleanup_duplicate_declarations(self, html_content: str) -> str:
        """Clean up duplicate reportData declarations"""
        try:
            logger.info("Cleaning up duplicate data declarations...")
            
            # Find all reportData declarations
            reportdata_pattern = r'\b(const|let|var)\s+reportData\s*=\s*\{[\s\S]*?\}\s*;?'
            window_pattern = r'window\.(pageData|reportData)\s*=\s*\{[\s\S]*?\}\s*;?'
            
            reportdata_matches = list(re.finditer(reportdata_pattern, html_content, re.IGNORECASE))
            window_matches = list(re.finditer(window_pattern, html_content, re.IGNORECASE))
            
            logger.info(f"Found {len(reportdata_matches)} reportData declarations and {len(window_matches)} window declarations")
            
            # Keep only the first reportData declaration
            if len(reportdata_matches) > 1:
                # Remove all but the first
                for match in reversed(reportdata_matches[1:]):
                    start, end = match.span()
                    html_content = html_content[:start] + html_content[end:]
                    logger.info(f"Removed duplicate reportData declaration at position {start}-{end}")
            
            # Keep only the first window declaration
            if len(window_matches) > 1:
                # Remove all but the first
                for match in reversed(window_matches[1:]):
                    start, end = match.span()
                    html_content = html_content[:start] + html_content[end:]
                    logger.info(f"Removed duplicate window declaration at position {start}-{end}")
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicate declarations: {e}")
            return html_content
    
    def _validate_html_structure(self, html_content: str) -> bool:
        """Validate basic HTML structure"""
        try:
            # Check for basic HTML structure
            has_doctype = bool(re.search(r'<!DOCTYPE\s+html', html_content, re.IGNORECASE))
            has_html_tag = bool(re.search(r'<html[^>]*>', html_content, re.IGNORECASE))
            has_head_tag = bool(re.search(r'<head[^>]*>', html_content, re.IGNORECASE))
            has_body_tag = bool(re.search(r'<body[^>]*>', html_content, re.IGNORECASE))
            has_charset = bool(re.search(r'<meta\s+charset', html_content, re.IGNORECASE))
            
            validation_results = {
                'doctype': has_doctype,
                'html_tag': has_html_tag,
                'head_tag': has_head_tag,
                'body_tag': has_body_tag,
                'charset': has_charset
            }
            
            logger.info(f"HTML structure validation: {validation_results}")
            
            # All should be True for valid HTML
            is_valid = all(validation_results.values())
            
            if not is_valid:
                missing = [k for k, v in validation_results.items() if not v]
                logger.warning(f"HTML structure validation failed, missing: {missing}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating HTML structure: {e}")
            return False

    def _is_report_path(self, filepath: str) -> bool:
        """检查是否为报告路径"""
        return filepath.startswith("report/") or "report" in filepath
    
    def _save_with_report_manager(self, html_content: str, filepath: str, data: Optional[Dict] = None) -> str:
        """使用报告管理器保存HTML"""
        try:
            # 从数据中提取股票代码
            stock_code = "unknown"
            if data and isinstance(data, dict):
                stock_code = data.get("stock_code", "unknown")
            
            # 准备元数据
            metadata = {
                "original_path": filepath,
                "content_type": "html",
                "data_size": len(html_content.encode('utf-8')),
                "has_data": bool(data),
                "generated_by": "create_html_tool"
            }
            
            if data:
                metadata["data_keys"] = list(data.keys()) if isinstance(data, dict) else []
            
            # 使用新的HTML报告保存方法
            success = report_manager.save_html_report(
                stock_code=stock_code,
                html_content=html_content,
                metadata=metadata
            )
            
            if success:
                # 生成预期的文件路径
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"html_{stock_code}_{timestamp}.html"
                saved_path = report_manager.get_report_path("html", filename)
                logger.info(f"HTML report saved to: {saved_path}")
                return f"HTML report saved to: {saved_path}"
            else:
                return "Failed to save HTML report"
                
        except Exception as e:
            error_msg = f"Failed to save HTML report: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _save_html_to_file(self, html_content: str, filepath: str) -> str:
        """Save generated HTML to a file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # Save with UTF-8 encoding
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            return f"HTML successfully saved to: {filepath}"
        except Exception as e:
            logger.error(f"Error saving HTML file: {e}")
            return f"Failed to save HTML file: {e}"

    async def execute(
        self,
        request: str,
        data: Optional[Dict[str, Any]] = None,
        output_path: str = "",
        reference: str = "",
        additional_requirements: str = "",
        **kwargs,
    ) -> ToolResult:
        """Execute HTML generation operation with enhanced error handling and validation

        Args:
            request: Detailed description of the HTML page requirements
            data: Optional data to display in the page
            output_path: Optional path to save the HTML file
            reference: Optional reference design or layout
            additional_requirements: Optional additional requirements

        Returns:
            ToolResult: Result containing the generated HTML or error message
        """
        try:
            logger.info(f"Starting HTML generation for request: {request[:100]}...")
            
            # Validate input parameters
            if not request or not request.strip():
                raise ValueError("Request cannot be empty")
            
            # Prepare additional context
            additional_context = {}
            if data:
                additional_context["data"] = data
                logger.info(f"Data provided with keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")
            if reference:
                additional_context["reference"] = reference
                logger.info("Reference design provided")
            if additional_requirements:
                additional_context["requirements"] = additional_requirements
                logger.info("Additional requirements provided")

            # Generate HTML
            logger.info("Generating HTML content...")
            html_content = await self._generate_html(
                request=request,
                additional_context=additional_context if additional_context else None,
            )
            
            if not html_content or not html_content.strip():
                raise ValueError("Generated HTML content is empty")
            
            logger.info(f"HTML generated successfully, length: {len(html_content)}")
            
            # Validate HTML structure
            is_valid_structure = self._validate_html_structure(html_content)
            if not is_valid_structure:
                logger.warning("Generated HTML has structural issues, but proceeding...")
            
            # Inject data into HTML if available
            if data:
                logger.info("Injecting data into HTML...")
                original_length = len(html_content)
                html_content = self._inject_data_into_html(html_content, data)
                logger.info(f"Data injection completed, length change: {len(html_content) - original_length}")
            
            # Final validation
            final_validation = self._validate_html_structure(html_content)
            logger.info(f"Final HTML validation: {'✅ PASSED' if final_validation else '⚠️ ISSUES DETECTED'}")

            # Save to file if path provided
            result_message = ""
            if output_path:
                logger.info(f"Saving HTML to: {output_path}")
                try:
                    # 优先使用报告管理器保存
                    if self._is_report_path(output_path):
                        save_result = self._save_with_report_manager(
                            html_content, output_path, data
                        )
                    else:
                        save_result = await self._save_html_to_file(
                            html_content=html_content, filepath=output_path
                        )
                    result_message = f"\n{save_result}"
                    logger.info(f"File saved successfully: {save_result}")
                except Exception as save_error:
                    logger.error(f"Failed to save file: {save_error}")
                    result_message = f"\nWarning: Failed to save file - {save_error}"

            # Prepare success result
            success_message = f"HTML generation successful, length: {len(html_content)} characters"
            if not final_validation:
                success_message += " (with structural warnings)"
            success_message += result_message
            
            logger.info("HTML generation completed successfully")
            
            # Return success result
            return ToolResult(
                output={
                    "html_content": html_content,
                    "saved_to": output_path if output_path else None,
                    "message": success_message,
                    "validation_passed": final_validation,
                    "content_length": len(html_content)
                }
            )

        except Exception as e:
            error_msg = f"HTML generation failed: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return detailed error information
            return ToolResult(
                error=error_msg,
                output={
                    "error_type": type(e).__name__,
                    "error_details": str(e),
                    "request_length": len(request) if request else 0,
                    "has_data": bool(data),
                    "output_path": output_path
                }
            )
