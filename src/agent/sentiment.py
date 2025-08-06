from typing import Any, List, Optional, Dict

from pydantic import Field

from src.agent.mcp import MCPAgent
from src.prompt.mcp import NEXT_STEP_PROMPT_ZN
from src.prompt.sentiment import SENTIMENT_SYSTEM_PROMPT
from src.schema import Message
from src.tool import Terminate, ToolCollection
from src.tool.sentiment import SentimentTool
from src.tool.web_search import WebSearch

import logging
logger = logging.getLogger(__name__)


class SentimentAgent(MCPAgent):
    """Sentiment analysis agent focused on market sentiment and news."""

    name: str = "sentiment_agent"
    description: str = "Analyzes market sentiment, news, and social media for insights on stock performance."
    system_prompt: str = SENTIMENT_SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT_ZN

    # Initialize with FinGenius tools with proper type annotation
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            SentimentTool(),
            WebSearch(),
            Terminate(),
        )
    )

    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    async def run(
        self, request: Optional[str] = None, stock_code: Optional[str] = None
    ) -> Any:
        """Run sentiment analysis on the given stock.

        Args:
            request: Optional initial request to process. If provided, overrides stock_code parameter.
            stock_code: The stock code/ticker to analyze

        Returns:
            Dictionary containing sentiment analysis results
        """
        # If stock_code is provided but request is not, create request from stock_code
        if stock_code and not request:
            # Set up system message about the stock being analyzed
            self.memory.add_message(
                Message.system_message(
                    f"你正在分析股票 {stock_code} 的市场情绪。请收集相关新闻、社交媒体数据，并评估整体情绪。"
                )
            )
            request = f"请分析 {stock_code} 的市场情绪和相关新闻。"

        # Call parent implementation with the request
        return await super().run(request)

    async def analyze(self, stock_code: str, **kwargs) -> Dict:
        """执行舆情分析"""
        try:
            logger.info(f"开始舆情分析: {stock_code}")
            
            # 确保工具执行 - 添加强制执行逻辑
            analysis_tasks = []
            
            # 1. 强制执行新闻搜索
            try:
                news_result = await self.available_tools.execute(
                    name="web_search", 
                    tool_input={
                        "query": f"{stock_code} 股票 最新消息 舆情",
                        "max_results": 10
                    }
                )
                if news_result and not news_result.error:
                    analysis_tasks.append(("news_search", news_result.output))
                    logger.info(f"新闻搜索成功: {stock_code}")
                else:
                    logger.warning(f"新闻搜索失败: {stock_code}, {news_result.error if news_result else 'Unknown error'}")
            except Exception as e:
                logger.error(f"新闻搜索异常: {stock_code}, {str(e)}")
            
            # 2. 强制执行社交媒体分析
            try:
                social_result = await self.available_tools.execute(
                    name="web_search", 
                    tool_input={
                        "query": f"{stock_code} 股吧 讨论 情绪",
                        "max_results": 5
                    }
                )
                if social_result and not social_result.error:
                    analysis_tasks.append(("social_media", social_result.output))
                    logger.info(f"社交媒体分析成功: {stock_code}")
                else:
                    logger.warning(f"社交媒体分析失败: {stock_code}, {social_result.error if social_result else 'Unknown error'}")
            except Exception as e:
                logger.error(f"社交媒体分析异常: {stock_code}, {str(e)}")
            
            # 3. 强制执行舆情分析工具
            try:
                sentiment_result = await self.available_tools.execute(
                    name="sentiment_analysis", 
                    tool_input={
                        "stock_code": stock_code,
                        "analysis_type": "comprehensive"
                    }
                )
                if sentiment_result and not sentiment_result.error:
                    analysis_tasks.append(("sentiment_analysis", sentiment_result.output))
                    logger.info(f"舆情分析工具成功: {stock_code}")
                else:
                    logger.warning(f"舆情分析工具失败: {stock_code}, {sentiment_result.error if sentiment_result else 'Unknown error'}")
            except Exception as e:
                logger.error(f"舆情分析工具异常: {stock_code}, {str(e)}")
            
            # 4. 综合分析结果
            if analysis_tasks:
                summary = self._generate_comprehensive_summary(analysis_tasks, stock_code)
                logger.info(f"舆情分析完成: {stock_code}, 执行了 {len(analysis_tasks)} 个任务")
                return {
                    "success": True,
                    "analysis_count": len(analysis_tasks),
                    "summary": summary,
                    "tasks_executed": [task[0] for task in analysis_tasks]
                }
            else:
                logger.warning(f"舆情分析没有成功执行任何任务: {stock_code}")
                return {
                    "success": False,
                    "analysis_count": 0,
                    "summary": "无法获取舆情数据，请检查网络连接和数据源",
                    "tasks_executed": []
                }
                
        except Exception as e:
            logger.error(f"舆情分析失败: {stock_code}, {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_count": 0,
                "summary": f"舆情分析异常: {str(e)}"
            }
    
    def _generate_comprehensive_summary(self, analysis_tasks: List, stock_code: str) -> str:
        """生成综合舆情分析报告"""
        try:
            summary_parts = [f"## {stock_code} 舆情分析报告\n"]
            
            for task_name, task_data in analysis_tasks:
                if task_name == "news_search":
                    summary_parts.append("### 📰 新闻舆情")
                    summary_parts.append(f"- 搜索到 {len(task_data.get('results', []))} 条相关新闻")
                    summary_parts.append(f"- 整体情绪倾向: {self._analyze_news_sentiment(task_data)}")
                    
                elif task_name == "social_media":
                    summary_parts.append("### 💬 社交媒体情绪")
                    summary_parts.append(f"- 搜索到 {len(task_data.get('results', []))} 条相关讨论")
                    summary_parts.append(f"- 投资者情绪: {self._analyze_social_sentiment(task_data)}")
                    
                elif task_name == "sentiment_analysis":
                    summary_parts.append("### 📊 专业舆情分析")
                    summary_parts.append(f"- 情绪指数: {task_data.get('sentiment_score', 'N/A')}")
                    summary_parts.append(f"- 风险等级: {task_data.get('risk_level', 'N/A')}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成舆情分析报告失败: {str(e)}")
            return f"舆情分析报告生成失败: {str(e)}"
    
    def _analyze_news_sentiment(self, data: Dict) -> str:
        """分析新闻情绪"""
        try:
            results = data.get('results', [])
            if not results:
                return "中性"
            
            # 简单的关键词情绪分析
            positive_keywords = ["上涨", "利好", "突破", "增长", "看好"]
            negative_keywords = ["下跌", "利空", "暴跌", "风险", "亏损"]
            
            positive_count = 0
            negative_count = 0
            
            for result in results:
                text = result.get('snippet', '') + result.get('title', '')
                for keyword in positive_keywords:
                    if keyword in text:
                        positive_count += 1
                for keyword in negative_keywords:
                    if keyword in text:
                        negative_count += 1
            
            if positive_count > negative_count:
                return "偏正面"
            elif negative_count > positive_count:
                return "偏负面"
            else:
                return "中性"
        except:
            return "中性"
    
    def _analyze_social_sentiment(self, data: Dict) -> str:
        """分析社交媒体情绪"""
        try:
            results = data.get('results', [])
            if not results:
                return "平淡"
            
            # 简单的讨论热度分析
            discussion_keywords = ["买入", "卖出", "持有", "看涨", "看跌"]
            keyword_count = 0
            
            for result in results:
                text = result.get('snippet', '') + result.get('title', '')
                for keyword in discussion_keywords:
                    if keyword in text:
                        keyword_count += 1
            
            if keyword_count >= 5:
                return "活跃"
            elif keyword_count >= 2:
                return "一般"
            else:
                return "平淡"
        except:
            return "平淡"
