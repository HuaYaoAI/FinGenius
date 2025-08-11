# !/usr/bin/env python3
import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.environment.battle import BattleEnvironment
from src.environment.research import ResearchEnvironment
from src.logger import logger
from src.schema import AgentState
from src.tool.tts_tool import TTSTool
from src.agent.report import ReportAgent
from src.utils.report_manager import report_manager
from src.console import visualizer, clear_screen
from rich.console import Console

console = Console()


class EnhancedFinGeniusAnalyzer:
    """Enhanced FinGenius analyzer with beautiful visualization"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_tool_calls = 0
        self.total_llm_calls = 0

    async def analyze_stock(self, stock_code: str, max_steps: int = 3, debate_rounds: int = 2) -> Dict[str, Any]:
        """Run complete stock analysis with enhanced visualization"""
        try:
            # Clear screen and show logo
            clear_screen()
            visualizer.show_logo()
            
            # Show analysis start
            visualizer.show_section_header("开始股票分析", "🚀")
            visualizer.show_progress_update("初始化分析环境", f"目标股票: {stock_code}")
            
            # Research phase
            visualizer.show_section_header("研究阶段", "🔍")
            research_results = await self._run_research_phase(stock_code, max_steps)
            
            if not research_results:
                visualizer.show_error("研究阶段失败", "无法获取足够的分析数据")
                return {"error": "Research failed", "stock_code": stock_code}
            
            # Show research results
            visualizer.show_research_summary(research_results)
            
            # Battle phase
            visualizer.show_section_header("专家辩论阶段", "⚔️")
            battle_results = await self._run_battle_phase(research_results, max_steps, debate_rounds)
            
            if battle_results:
                visualizer.show_debate_summary(battle_results)
            
            # Generate reports
            await self._generate_reports(stock_code, research_results, battle_results)
            
            # Final results
            final_results = self._prepare_final_results(stock_code, research_results, battle_results)
            
            # Show completion
            total_time = time.time() - self.start_time
            visualizer.show_completion(total_time)
            
            return final_results
            
        except Exception as e:
            visualizer.show_error(str(e), "股票分析过程中出现错误")
            logger.error(f"Analysis failed: {str(e)}")
            return {"error": str(e), "stock_code": stock_code}

    async def _run_research_phase(self, stock_code: str, max_steps: int) -> Dict[str, Any]:
        """Run research phase with enhanced visualization"""
        try:
            # Create research environment
            visualizer.show_progress_update("创建研究环境")
            # agent interval is injected from instance attribute if set
            interval = getattr(self, "agent_interval_seconds", 3)
            research_env = await ResearchEnvironment.create(max_steps=max_steps, agent_interval_seconds=interval)
            
            # Show registered agents
            agent_names = [
                "sentiment_agent",
                "risk_control_agent", 
                "hot_money_agent",
                "technical_analysis_agent",
                "chip_analysis_agent",
                "big_deal_analysis_agent",
            ]
            
            for name in agent_names:
                agent = research_env.get_agent(name)
                if agent:
                    visualizer.show_progress_update(f"注册研究员", f"专家: {agent.name}")
            
            # Run research with tool call visualization
            visualizer.show_progress_update("开始深度研究", f"多专家顺序分析中（每{interval}秒一个）...")
            
            # Enhance agents with visualization
            self._enhance_agents_with_visualization(research_env)
            
            results = await research_env.run(stock_code)
            
            # Update counters
            if hasattr(research_env, 'tool_calls'):
                self.total_tool_calls += research_env.tool_calls
            if hasattr(research_env, 'llm_calls'):
                self.total_llm_calls += research_env.llm_calls
            
            await research_env.cleanup()
            return results
            
        except Exception as e:
            visualizer.show_error(f"研究阶段错误: {str(e)}")
            return {}

    async def _run_battle_phase(self, research_results: Dict[str, Any], max_steps: int, debate_rounds: int) -> Dict[str, Any]:
        """Run battle phase with enhanced visualization"""
        try:
            # Create battle environment
            visualizer.show_progress_update("创建辩论环境")
            battle_env = await BattleEnvironment.create(max_steps=max_steps, debate_rounds=debate_rounds)
            
            # Register agents for battle
            research_env = await ResearchEnvironment.create(max_steps=max_steps)
            agent_names = [
                "sentiment_agent",
                "risk_control_agent",
                "hot_money_agent", 
                "technical_analysis_agent",
                "chip_analysis_agent",
                "big_deal_analysis_agent",
            ]
            
            for name in agent_names:
                agent = research_env.get_agent(name)
                if agent:
                    agent.current_step = 0
                    agent.state = AgentState.IDLE
                    battle_env.register_agent(agent)
                    visualizer.show_progress_update(f"注册辩论专家", f"专家: {agent.name}")
            
            # Enhance agents with visualization for battle
            self._enhance_battle_agents_with_visualization(battle_env)
            
            # Run battle
            visualizer.show_progress_update("开始专家辩论", "多轮辩论与投票中...")
            results = await battle_env.run(research_results)
            
            # Update counters
            if hasattr(battle_env, 'tool_calls'):
                self.total_tool_calls += battle_env.tool_calls
            if hasattr(battle_env, 'llm_calls'):
                self.total_llm_calls += battle_env.llm_calls
            
            await research_env.cleanup()
            await battle_env.cleanup()
            return results
            
        except Exception as e:
            visualizer.show_error(f"辩论阶段错误: {str(e)}")
            return {}

    def _enhance_agents_with_visualization(self, environment):
        """Simple visualization enhancement without breaking functionality"""
        # Don't override methods - just store agent names for later use
        pass

    def _enhance_battle_agents_with_visualization(self, battle_env):
        """Enhance battle agents with visualization for debate messages"""
        # Instead of overriding methods, we'll enhance the broadcast message method
        if hasattr(battle_env, '_broadcast_message'):
            original_broadcast = battle_env._broadcast_message
            
            async def enhanced_broadcast(sender_id: str, content: str, event_type: str):
                # Show the debate message before broadcasting
                agent_name = battle_env.state.active_agents.get(sender_id, sender_id)
                
                if event_type == "speak":
                    visualizer.show_debate_message(agent_name, content, "speak")
                elif event_type == "vote":
                    visualizer.show_debate_message(agent_name, f"投票 {content}", "vote")
                
                # Call original broadcast
                return await original_broadcast(sender_id, content, event_type)
            
            battle_env._broadcast_message = enhanced_broadcast

    async def _generate_reports(self, stock_code: str, research_result: Dict[str, Any], battle_result: Dict[str, Any]):
        """Generate reports with progress visualization"""
        try:
            visualizer.show_progress_update("生成分析报告", "创建HTML报告和JSON数据...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generate HTML report
            logger.info("生成HTML报告...")
            report_agent = await ReportAgent.create(max_steps=3)
            
            # Prepare report data
            summary = "\n\n".join([
                f"金融专家对{stock_code}的研究结果如下：",
                f"情感分析：{research_result.get('sentiment', '暂无数据')}",
                f"风险分析：{research_result.get('risk', '暂无数据')}",
                f"游资分析：{research_result.get('hot_money', '暂无数据')}",
                f"技术面分析：{research_result.get('technical', '暂无数据')}",
                f"筹码分析：{research_result.get('chip_analysis', '暂无数据')}",
                f"大单异动分析：{research_result.get('big_deal', '暂无数据')}",
                f"博弈结果：{battle_result.get('final_decision', '无结果')}",
                f"投票统计：{battle_result.get('vote_count', {})}"
            ])
            
            # Calculate vote percentages
            bull_cnt = battle_result.get('vote_count', {}).get('bullish', 0)
            bear_cnt = battle_result.get('vote_count', {}).get('bearish', 0)
            total_votes = bull_cnt + bear_cnt
            bull_pct = round(bull_cnt / total_votes * 100, 1) if total_votes else 0
            bear_pct = round(bear_cnt / total_votes * 100, 1) if total_votes else 0

            # Generate HTML report
            html_filename = f"report_{stock_code}_{timestamp}.html"
            html_path = f"report/{html_filename}"

            html_request = f"""
            基于股票{stock_code}的综合分析，生成一份美观的HTML报告。
            
            请在报告中包含以下模块，并按顺序呈现：
            1. 标题及股票基本信息
            2. 博弈结果与投票统计（先展示投票结论与统计）
               • 最终结论：{battle_result.get('final_decision', '未知')}
               • 看涨票数：{bull_cnt}（{bull_pct}%）
               • 看跌票数：{bear_cnt}（{bear_pct}%）
            3. 各项研究分析结果（情感、风险、游资、技术面、筹码、大单异动）
            4. 辩论对话过程：按照时间顺序，以聊天气泡或时间线形式展示 `battle_results.debate_history` 中的发言，**必须完整呈现全部发言，不得删减省略**；清晰标注轮次、专家名称、发言内容与时间戳。
            5. 任何你认为有助于读者理解的图表或可视化。
            
            重要：请确保页面最底部保留 AI 免责声明。
            """
            
            try:
                if report_agent and report_agent.available_tools:
                    await report_agent.available_tools.execute(
                        name="create_html",
                        tool_input={
                            "request": html_request,
                            "output_path": html_path,
                            "data": {
                                "stock_code": stock_code,
                                "research_results": research_result,
                                "battle_results": battle_result,
                                "timestamp": timestamp
                            }
                        }
                    )
                    visualizer.show_progress_update("HTML报告生成完成", f"文件: {html_path}")
                else:
                    logger.error("无法创建报告Agent或工具集")
            except Exception as e:
                logger.error(f"生成HTML报告失败: {str(e)}")
            
            # Save debate JSON
            visualizer.show_progress_update("保存辩论记录", "JSON格式...")
            debate_data = {
                "stock_code": stock_code,
                "timestamp": timestamp,
                "debate_rounds": battle_result.get("debate_rounds", 0),
                "agent_order": battle_result.get("agent_order", []),
                "debate_history": battle_result.get("debate_history", []),
                "battle_highlights": battle_result.get("battle_highlights", [])
            }
            
            report_manager.save_debate_report(
                stock_code=stock_code,
                debate_data=debate_data,
                metadata={
                    "type": "debate_dialog",
                    "debate_rounds": battle_result.get("debate_rounds", 0),
                    "participants": len(battle_result.get("agent_order", []))
                }
            )
            
            # Save vote results JSON
            visualizer.show_progress_update("保存投票结果", "JSON格式...")
            vote_data = {
                "stock_code": stock_code,
                "timestamp": timestamp,
                "final_decision": battle_result.get("final_decision", "No decision"),
                "vote_count": battle_result.get("vote_count", {}),
                "agent_order": battle_result.get("agent_order", []),
                "vote_details": {
                    "bullish": battle_result.get("vote_count", {}).get("bullish", 0),
                    "bearish": battle_result.get("vote_count", {}).get("bearish", 0),
                    "total_agents": len(battle_result.get("agent_order", []))
                }
            }
            
            report_manager.save_vote_report(
                stock_code=stock_code,
                vote_data=vote_data,
                metadata={
                    "type": "vote_results",
                    "final_decision": battle_result.get("final_decision", "No decision"),
                    "total_votes": sum(battle_result.get("vote_count", {}).values())
                }
            )
            
            visualizer.show_progress_update("报告生成完成", "所有文件已保存")
            
        except Exception as e:
            visualizer.show_error(f"生成报告失败: {str(e)}")

    def _prepare_final_results(self, stock_code: str, research_results: Dict[str, Any], battle_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare final analysis results"""
        final_results = {
            "stock_code": stock_code,
            "analysis_time": time.time() - self.start_time,
            "total_tool_calls": self.total_tool_calls,
            "total_llm_calls": self.total_llm_calls
        }
        
        # Merge research results
        if research_results:
            final_results.update(research_results)
        
        # Add battle insights
        if battle_results and "vote_count" in battle_results:
            votes = battle_results["vote_count"]
            total_votes = sum(votes.values())
            if total_votes > 0:
                bullish_pct = (votes.get("bullish", 0) / total_votes) * 100
                final_results["expert_consensus"] = f"{bullish_pct:.1f}% 看涨"
                final_results["battle_result"] = battle_results
        
        return final_results


async def announce_result_with_tts(results: Dict[str, Any]):
    """使用TTS工具播报最终的博弈结果"""
    try:
        battle_result = results.get("battle_result", {})
        final_decision = battle_result.get("final_decision", "Unknown")
        vote_count = battle_result.get("vote_count", {})
        stock_code = results.get("stock_code", "未知股票")

        if final_decision == "Unknown":
            tts_text = f"对{stock_code}的分析结果不明确，无法给出明确的建议。"
        else:
            bullish_count = vote_count.get("bullish", 0)
            bearish_count = vote_count.get("bearish", 0)

            if final_decision == "bullish":
                decision_text = "看涨"
            else:
                decision_text = "看跌"

            tts_text = f"股票{stock_code}的最终预测结果是{decision_text}。看涨票数{bullish_count}，看跌票数{bearish_count}。"

            # 添加一些关键战斗点
            if battle_result.get("battle_highlights"):
                tts_text += "关键分析点包括："
                for i, highlight in enumerate(
                    battle_result["battle_highlights"][:3]
                ):  # 只取前3个要点
                    agent = highlight.get("agent", "")
                    point = highlight.get("point", "")
                    tts_text += f"{agent}认为{point}。"

        # 初始化TTS工具并播报结果
        tts_tool = TTSTool()
        output_file = f"results/{stock_code}_result.mp3"

        # 执行TTS转换并播放
        await tts_tool.execute(text=tts_text, output_file=output_file)

        logger.info(f"结果语音播报已保存至: {output_file}")

    except Exception as e:
        logger.error(f"语音播报失败: {str(e)}")


def display_results(results: Dict[str, Any], output_format: str = "text", output_file: str | None = None):
    """Display or save research results."""
    # Handle JSON output
    if output_format == "json":
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    # For text output, results are already beautifully displayed during analysis
    # Just log completion
    if not output_file:
        return
    
    # Save to file if requested
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Stock Analysis Results for {results.get('stock_code', 'Unknown')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
    
    logger.info(f"Results saved to {output_file}")


async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="FinGenius Stock Research")
    parser.add_argument("stock_code", help="Stock code to research (e.g., AAPL, MSFT)")
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("-o", "--output", help="Save results to file")
    parser.add_argument(
        "--tts", action="store_true", help="Enable text-to-speech for the final result"
    )
    parser.add_argument(
        "--max-steps", 
        type=int, 
        default=3, 
        help="Maximum number of steps for each agent (default: 3)"
    )
    parser.add_argument(
        "--debate-rounds", 
        type=int, 
        default=2, 
        help="Number of debate rounds in battle (default: 2)"
    )
    parser.add_argument(
        "--agent-interval", 
        type=int, 
        default=3, 
        help="Seconds to wait between research agents (default: 3)"
    )

    args = parser.parse_args()
    analyzer = None

    try:
        # Create enhanced analyzer
        analyzer = EnhancedFinGeniusAnalyzer()
        # propagate interval so _run_research_phase can use it
        setattr(analyzer, "agent_interval_seconds", max(0, int(args.agent_interval)))
        
        # Run analysis with beautiful visualization
        results = await analyzer.analyze_stock(args.stock_code, args.max_steps, args.debate_rounds)
        
        # Display results
        display_results(results, args.format, args.output)

        # TTS announcement if requested
        if args.tts:
            import os
            os.makedirs("results", exist_ok=True)
            await announce_result_with_tts(results)

    except KeyboardInterrupt:
        visualizer.show_error("分析被用户中断", "Ctrl+C")
        return 1
    except Exception as e:
        visualizer.show_error(f"分析过程中发生错误: {str(e)}")
        logger.error(f"Error during research: {str(e)}")
        return 1
    finally:
        # Clean up resources to prevent warnings
        if analyzer:
            try:
                # Force cleanup of any remaining async resources
                import gc
                gc.collect()
                
                # Give time for cleanup
                await asyncio.sleep(0.1)
            except:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
