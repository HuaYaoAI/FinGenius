import asyncio
from typing import Any, Dict

from pydantic import Field

from src.agent.chip_analysis import ChipAnalysisAgent
from src.agent.hot_money import HotMoneyAgent
from src.agent.risk_control import RiskControlAgent
from src.agent.sentiment import SentimentAgent
from src.agent.technical_analysis import TechnicalAnalysisAgent
from src.agent.big_deal_analysis import BigDealAnalysisAgent
from src.environment.base import BaseEnvironment
from src.logger import logger
from src.schema import Message
from src.tool.stock_info_request import StockInfoRequest
from src.utils.report_manager import report_manager


class ResearchEnvironment(BaseEnvironment):
    """Environment for stock research using multiple specialized agents."""

    name: str = Field(default="research_environment")
    description: str = Field(default="Environment for comprehensive stock research")
    results: Dict[str, Any] = Field(default_factory=dict)
    max_steps: int = Field(default=3, description="Maximum steps for each agent")
    agent_interval_seconds: int = Field(default=3, description="Seconds to wait between agent runs")

    # Analysis mapping for agent roles
    analysis_mapping: Dict[str, str] = Field(
        default={
            "sentiment_agent": "sentiment",
            "risk_control_agent": "risk",
            "hot_money_agent": "hot_money",
            "technical_analysis_agent": "technical",
            "chip_analysis_agent": "chip_analysis",
            "big_deal_analysis_agent": "big_deal",
        }
    )

    async def initialize(self) -> None:
        """Initialize the research environment with specialized agents."""
        await super().initialize()

        # Create specialized analysis agents
        specialized_agents = {
            "sentiment_agent": await SentimentAgent.create(max_steps=self.max_steps),
            "risk_control_agent": await RiskControlAgent.create(max_steps=self.max_steps),
            "hot_money_agent": await HotMoneyAgent.create(max_steps=self.max_steps),
            "technical_analysis_agent": await TechnicalAnalysisAgent.create(max_steps=self.max_steps),
            "chip_analysis_agent": await ChipAnalysisAgent.create(max_steps=self.max_steps),
            "big_deal_analysis_agent": await BigDealAnalysisAgent.create(max_steps=self.max_steps),
        }

        # Register all agents
        for agent in specialized_agents.values():
            self.register_agent(agent)

        logger.info(f"Research environment initialized with 6 specialist agents (max_steps={self.max_steps})")

    async def run(self, stock_code: str) -> Dict[str, Any]:
        """Run research on the given stock code using all specialist agents."""
        logger.info(f"Running research on stock {stock_code}")

        try:
            # 获取股票基本信息
            basic_info_tool = StockInfoRequest()
            basic_info_result = await basic_info_tool.execute(stock_code=stock_code)

            if basic_info_result.error:
                logger.error(f"Error getting basic info: {basic_info_result.error}")
            else:
                # 将基本信息添加到每个agent的上下文中
                stock_info_message = f"""
                股票代码: {stock_code}
                当前交易日: {basic_info_result.output.get('current_trading_day', '未知')}
                基本信息: {basic_info_result.output.get('basic_info', '{}')}
                """

                for agent_key in self.analysis_mapping.keys():
                    agent = self.get_agent(agent_key)
                    if agent and hasattr(agent, "memory"):
                        agent.memory.add_message(
                            Message.system_message(stock_info_message)
                        )
                        logger.info(f"Added basic stock info to {agent_key}'s context")

            # Run analysis tasks sequentially with 3-second intervals
            results = {}
            agent_count = 0
            total_agents = len([k for k in self.analysis_mapping.keys() if k in self.agents])
            
            # Import visualizer for progress display
            try:
                from src.console import visualizer
                show_visual = True
            except:
                show_visual = False
            
            for agent_key, result_key in self.analysis_mapping.items():
                if agent_key not in self.agents:
                    continue
                    
                agent_count += 1
                logger.info(f"🔄 Starting analysis with {agent_key} ({agent_count}/{total_agents})")
                
                # Show agent starting in terminal
                if show_visual:
                    visualizer.show_agent_starting(agent_key, agent_count, total_agents)
                
                try:
                    # Run individual agent
                    result = await self.agents[agent_key].run(stock_code)
                    results[result_key] = result
                    logger.info(f"✅ Completed analysis with {agent_key}")
                    
                    # Show agent completion in terminal
                    if show_visual:
                        visualizer.show_agent_completed(agent_key, agent_count, total_agents)
                    
                    # Wait configured interval before next agent (except for the last one)
                    if agent_count < total_agents:
                        logger.info(f"⏳ Waiting {self.agent_interval_seconds} seconds before next agent...")
                        if show_visual:
                            visualizer.show_waiting_next_agent(self.agent_interval_seconds)
                        await asyncio.sleep(self.agent_interval_seconds)
                        
                except Exception as e:
                    logger.error(f"❌ Error with {agent_key}: {str(e)}")
                    results[result_key] = f"Error: {str(e)}"

            if not results:
                return {
                    "error": "No specialist agents completed successfully",
                    "stock_code": stock_code,
                }

            # 添加基本信息到结果中
            if not basic_info_result.error:
                results["basic_info"] = basic_info_result.output

            # Store and return complete results (without generating report here)
            self.results = {**results, "stock_code": stock_code}
            return self.results

        except Exception as e:
            logger.error(f"Error in research: {str(e)}")
            return {"error": str(e), "stock_code": stock_code}

    async def cleanup(self) -> None:
        """Clean up all agent resources."""
        cleanup_tasks = [
            agent.cleanup()
            for agent in self.agents.values()
            if hasattr(agent, "cleanup")
        ]

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks)

        await super().cleanup()
