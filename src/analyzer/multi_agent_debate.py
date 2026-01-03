"""
Multi-Agent Debate System - Real independent agents that debate and cross-validate each other.

This module implements a true multi-agent debate system where three independent AI agents
with distinct personas analyze the market and debate to reach a consensus decision.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio


@dataclass
class AgentOpinion:
    """Opinion from a single agent."""
    agent_name: str
    decision: str  # BUY/SELL/HOLD
    direction: str  # LONG/SHORT/NEUTRAL
    confidence: int  # 0-100
    reasoning: str
    take_profit: float
    stop_loss: float
    entry_price: float
    warnings: List[str]
    key_factors: List[str]


class MultiAgentDebateSystem:
    """
    Real multi-agent debate system with three independent agents:
    1. Aggressive Agent - Focuses on momentum and breakout opportunities
    2. Conservative Agent - Focuses on risk management and support/resistance
    3. Referee Agent - Synthesizes opinions and makes final decision
    """

    def __init__(self, model_manager, logger, context, prompt_builder):
        """
        Initialize the multi-agent debate system.

        Args:
            model_manager: AI model manager for API calls
            logger: Logger instance
            context: Market analysis context
            prompt_builder: Prompt builder for generating prompts
        """
        self.model_manager = model_manager
        self.logger = logger
        self.context = context
        self.prompt_builder = prompt_builder

    async def conduct_debate(
        self,
        symbol: str,
        current_price: float,
        provider: Optional[str] = None,  # Not used - each agent has fixed provider
        model: Optional[str] = None  # Not used - each agent has fixed model
    ) -> Dict[str, Any]:
        """
        Conduct a multi-agent debate and return the final decision.

        This method orchestrates the debate in three phases:
        1. Aggressive agent analyzes (Google AI → OpenRouter fallback)
        2. Conservative agent reviews aggressive opinion (Google AI → OpenRouter fallback)
        3. Referee agent synthesizes both opinions (Groq → OpenRouter fallback)

        Args:
            symbol: Trading pair symbol
            current_price: Current market price
            provider: Optional AI provider override (ignored - each agent has fixed provider)
            model: Optional AI model override (ignored - each agent has fixed model)

        Returns:
            Final decision dictionary with all agent opinions
        """
        self.logger.info("🎭 Starting Multi-Agent Debate System")
        self.logger.info("   🔴 Aggressive: Google AI → OpenRouter")
        self.logger.info("   🔵 Conservative: Google AI → OpenRouter")
        self.logger.info("   ⚖️ Referee: Google AI → OpenRouter")

        # Phase 1: Aggressive Agent Analysis (Google AI)
        self.logger.info("🔴 Phase 1: Aggressive Agent analyzing...")
        aggressive_opinion = await self._run_aggressive_agent(
            symbol, current_price
        )

        # Phase 2: Conservative Agent Review & Counter-Opinion (Google AI)
        self.logger.info("🔵 Phase 2: Conservative Agent reviewing and countering...")
        conservative_opinion = await self._run_conservative_agent(
            symbol, current_price, aggressive_opinion
        )

        # Phase 3: Referee Agent Final Judgment (Groq)
        self.logger.info("⚖️ Phase 3: Referee Agent making final judgment...")
        final_decision = await self._run_referee_agent(
            symbol, current_price, aggressive_opinion, conservative_opinion
        )

        # Log debate summary
        self._log_debate_summary(aggressive_opinion, conservative_opinion, final_decision)

        # Build result with proper validation and auto-correction
        result = {
            "decision": final_decision.get("decision", "HOLD"),
            "direction": final_decision.get("direction", "NEUTRAL"),
            "confidence": final_decision.get("confidence", 50),
            "reasoning": final_decision.get("reasoning", ""),
            "take_profit": final_decision.get("take_profit", current_price),
            "stop_loss": final_decision.get("stop_loss", current_price),
            "entry_price": final_decision.get("entry_price", current_price),
            "debate_transcript": {
                "aggressive": aggressive_opinion,
                "conservative": conservative_opinion,
                "referee": final_decision
            }
        }

        # Apply trade validation and auto-correction
        from src.utils.trade_validator import TradeValidator

        is_valid, error_msg, _ = TradeValidator.validate_trade_decision(result, current_price)

        if not is_valid:
            self.logger.warning(f"⚠️ Referee decision validation failed: {error_msg}")
            self.logger.info("🔧 Attempting auto-correction...")

            corrected_result = TradeValidator.auto_correct_direction(result, current_price, default_rr_ratio=1.5)

            # Re-validate corrected result
            is_valid_after, error_msg_after, _ = TradeValidator.validate_trade_decision(corrected_result, current_price)

            if is_valid_after:
                self.logger.info("✅ Auto-correction successful!")
                self.logger.info(f"   Entry: {corrected_result['entry_price']:.4f}")
                self.logger.info(f"   TP: {corrected_result['take_profit']:.4f}")
                self.logger.info(f"   SL: {corrected_result['stop_loss']:.4f}")
                return corrected_result
            else:
                self.logger.error(f"❌ Auto-correction failed: {error_msg_after}")
                self.logger.warning("⚠️ Falling back to HOLD decision for safety")
                result["decision"] = "HOLD"
                result["direction"] = "NEUTRAL"
                result["confidence"] = 0
                result["reasoning"] = f"Trade validation failed: {error_msg}"
                return result

        return result

    async def _run_aggressive_agent(
        self,
        symbol: str,
        current_price: float
    ) -> Dict[str, Any]:
        """
        Run the Aggressive Agent analysis.

        The Aggressive Agent focuses on:
        - Short-term momentum and volume explosions
        - Breakout opportunities
        - Entry opportunities even near resistance zones
        - Trigger timeframe strength

        Provider: Google AI → OpenRouter (fallback)

        Args:
            symbol: Trading pair
            current_price: Current price

        Returns:
            Aggressive agent's opinion
        """
        system_prompt = """You are the AGGRESSIVE AGENT in a multi-agent trading system.

YOUR ROLE:
- Focus on SHORT-TERM MOMENTUM and volume explosions
- Look for BREAKOUT opportunities and strong Trigger timeframe signals
- Argue that strong momentum can overcome resistance zones
- Be willing to take calculated risks for high-reward trades

YOUR PERSONALITY:
- Optimistic about strong momentum
- Confident in breakout potential
- Willing to enter near resistance if volume and momentum are strong
- Focus on R/R ratio and profit potential

OUTPUT FORMAT (JSON):
{
  "decision": "BUY|SELL|HOLD",
  "direction": "LONG|SHORT|NEUTRAL",
  "confidence": 0-100,
  "reasoning": "1-2 sentences explaining your aggressive stance",
  "take_profit": <price>,
  "stop_loss": <price>,
  "entry_price": <price>,
  "key_factors": ["momentum strength", "volume surge", "breakout potential"],
  "warnings": ["any risks you acknowledge"]
}

REMEMBER: You are ONE agent in a debate. Your opinion will be challenged by the Conservative Agent.
Be BOLD but RATIONAL. Provide specific price levels and clear reasoning."""

        user_prompt = self._build_market_data_prompt(symbol, current_price)
        user_prompt += "\n\nAs the AGGRESSIVE AGENT, provide your analysis and trading recommendation."

        # Call AI model with Google AI (fallback to OpenRouter if fails)
        response = await self.model_manager.send_prompt_streaming(
            prompt=user_prompt,
            system_message=system_prompt,
            provider="googleai",  # Fixed: Google AI
            model=None  # Use default model for provider
        )

        # Parse response
        parsed = self._parse_agent_response(response, "Aggressive")
        return parsed

    async def _run_conservative_agent(
        self,
        symbol: str,
        current_price: float,
        aggressive_opinion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the Conservative Agent analysis.

        The Conservative Agent:
        - Reviews the Aggressive Agent's opinion
        - Focuses on risk management and S/R zones
        - Challenges overly aggressive entries
        - Provides counter-arguments and warnings

        Provider: Google AI → OpenRouter (fallback)

        Args:
            symbol: Trading pair
            current_price: Current price
            aggressive_opinion: Opinion from Aggressive Agent

        Returns:
            Conservative agent's opinion
        """
        system_prompt = """You are the CONSERVATIVE AGENT in a multi-agent trading system.

YOUR ROLE:
- Focus on RISK MANAGEMENT and strong S/R supply/demand zones
- Challenge the Aggressive Agent's opinion with COUNTER-ARGUMENTS
- Look for danger signals and proximity to resistance/support walls
- Prioritize capital preservation and high-probability setups

YOUR PERSONALITY:
- Skeptical of overly optimistic momentum plays
- Careful about entries near strong resistance/support
- Focus on what can go WRONG
- Demand higher confluence and safer entry points

YOU WILL RECEIVE:
- The Aggressive Agent's opinion
- Market data

YOUR TASK:
- Directly address the Aggressive Agent's arguments
- Point out risks they may have overlooked
- Provide your own counter-recommendation

OUTPUT FORMAT (JSON):
{
  "decision": "BUY|SELL|HOLD",
  "direction": "LONG|SHORT|NEUTRAL",
  "confidence": 0-100,
  "reasoning": "1-2 sentences ADDRESSING aggressive opinion and your concerns",
  "take_profit": <price>,
  "stop_loss": <price>,
  "entry_price": <price>,
  "key_factors": ["proximity to S/R", "risk level", "trend strength"],
  "warnings": ["specific dangers you see"],
  "rebuttal_to_aggressive": "Direct response to Aggressive Agent's argument"
}

REMEMBER: You are the VOICE OF CAUTION. Challenge weak arguments. Protect capital."""

        user_prompt = self._build_market_data_prompt(symbol, current_price)
        user_prompt += f"\n\n--- AGGRESSIVE AGENT'S OPINION ---\n"
        user_prompt += f"Decision: {aggressive_opinion.get('decision', 'UNKNOWN')}\n"
        user_prompt += f"Direction: {aggressive_opinion.get('direction', 'UNKNOWN')}\n"
        user_prompt += f"Confidence: {aggressive_opinion.get('confidence', 0)}%\n"
        user_prompt += f"Reasoning: {aggressive_opinion.get('reasoning', 'N/A')}\n"
        user_prompt += f"Entry: {aggressive_opinion.get('entry_price', current_price)}\n"
        user_prompt += f"TP: {aggressive_opinion.get('take_profit', 0)}\n"
        user_prompt += f"SL: {aggressive_opinion.get('stop_loss', 0)}\n"
        user_prompt += "\n\nAs the CONSERVATIVE AGENT, review the Aggressive Agent's opinion and provide YOUR counter-analysis."

        # Call AI model with Google AI (fallback to OpenRouter if fails)
        response = await self.model_manager.send_prompt_streaming(
            prompt=user_prompt,
            system_message=system_prompt,
            provider="googleai",  # Fixed: Google AI
            model=None  # Use default model for provider
        )

        # Parse response
        parsed = self._parse_agent_response(response, "Conservative")
        return parsed

    async def _run_referee_agent(
        self,
        symbol: str,
        current_price: float,
        aggressive_opinion: Dict[str, Any],
        conservative_opinion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the Referee Agent to make final decision.

        The Referee Agent:
        - Reviews both agents' opinions
        - Weighs the arguments from both sides
        - Makes a balanced final decision
        - Can side with either agent or find middle ground

        Provider: Google AI → OpenRouter (fallback)

        Args:
            symbol: Trading pair
            current_price: Current price
            aggressive_opinion: Opinion from Aggressive Agent
            conservative_opinion: Opinion from Conservative Agent

        Returns:
            Referee's final decision
        """
        system_prompt = """You are the REFEREE AGENT in a multi-agent trading system.

YOUR ROLE:
- Review BOTH the Aggressive and Conservative agents' opinions
- Weigh the arguments from BOTH sides objectively
- Make a BALANCED final decision
- You can agree with one side, find middle ground, or create a synthesis

YOUR DECISION CRITERIA:
1. Risk/Reward ratio (must be >= 1.5:1)
2. Multi-timeframe alignment (2+ timeframes aligned = stronger signal)
3. Momentum strength vs S/R proximity
4. Overall confluence of factors

OUTPUT FORMAT (JSON):
{
  "decision": "BUY|SELL|HOLD",
  "direction": "LONG|SHORT|NEUTRAL",
  "confidence": 0-100,
  "reasoning": "2-3 sentences explaining which agent you sided with and WHY",
  "take_profit": <price>,
  "stop_loss": <price>,
  "entry_price": <price>,
  "verdict": "Aggressive|Conservative|Compromise",
  "key_reasoning": "Specific factors that led to your decision"
}

REMEMBER:
- You are the FINAL ARBITER
- Your decision is BINDING
- Explain clearly which arguments won and why
- Ensure TP/SL make sense (LONG: SL < entry < TP, SHORT: TP < entry < SL)"""

        # Build detailed prompt for Referee with FULL analysis from both agents
        user_prompt = f"""Symbol: {symbol}
Current Price: ${current_price:,.2f}

=== COMPLETE DEBATE ANALYSIS ===

🔴 AGGRESSIVE AGENT'S FULL ANALYSIS:
Decision: {aggressive_opinion.get('decision', 'UNKNOWN')} {aggressive_opinion.get('direction', 'NEUTRAL')}
Confidence: {aggressive_opinion.get('confidence', 0)}%
Entry Price: ${aggressive_opinion.get('entry_price', current_price):,.2f}
Take Profit: ${aggressive_opinion.get('take_profit', 0):,.2f}
Stop Loss: ${aggressive_opinion.get('stop_loss', 0):,.2f}

Full Reasoning:
{aggressive_opinion.get('reasoning', 'N/A')}

Key Factors:
{', '.join(aggressive_opinion.get('key_factors', ['N/A']))}

Momentum Indicators:
{', '.join(aggressive_opinion.get('momentum_indicators', ['N/A']))}

---

🔵 CONSERVATIVE AGENT'S FULL ANALYSIS:
Decision: {conservative_opinion.get('decision', 'UNKNOWN')} {conservative_opinion.get('direction', 'NEUTRAL')}
Confidence: {conservative_opinion.get('confidence', 0)}%
Entry Price: ${conservative_opinion.get('entry_price', current_price):,.2f}
Take Profit: ${conservative_opinion.get('take_profit', 0):,.2f}
Stop Loss: ${conservative_opinion.get('stop_loss', 0):,.2f}

Full Reasoning:
{conservative_opinion.get('reasoning', 'N/A')}

Key Factors:
{', '.join(conservative_opinion.get('key_factors', ['N/A']))}

Warnings:
{', '.join(conservative_opinion.get('warnings', ['N/A']))}

Rebuttal to Aggressive Agent:
{conservative_opinion.get('rebuttal_to_aggressive', 'None')}

---

As the REFEREE, review BOTH agents' COMPLETE analyses and make your FINAL BINDING DECISION."""

        # Call AI model with Google AI (fallback to OpenRouter if fails)
        response = await self.model_manager.send_prompt_streaming(
            prompt=user_prompt,
            system_message=system_prompt,
            provider="googleai",  # Fixed: Google AI (same as other agents)
            model=None  # Use default model for provider
        )

        # Parse response
        parsed = self._parse_agent_response(response, "Referee")
        return parsed

    def _build_market_data_prompt(self, symbol: str, current_price: float) -> str:
        """Build the market data section of the prompt."""
        # Use existing prompt builder to get market context
        # This reuses the existing technical analysis and market data formatting
        market_prompt = self.prompt_builder.build_prompt(
            context=self.context,
            has_chart_analysis=False,
            additional_context=None,
            previous_indicators=None
        )

        return f"Symbol: {symbol}\nCurrent Price: {current_price}\n\n{market_prompt}"

    def _parse_agent_response(self, response: str, agent_name: str) -> Dict[str, Any]:
        """
        Parse agent response from JSON.

        Args:
            response: Raw AI response
            agent_name: Name of the agent

        Returns:
            Parsed opinion dictionary
        """
        import json
        import re

        # DEBUG: Log raw response details
        self.logger.debug(f"[{agent_name}] Raw response length: {len(response)} chars")
        self.logger.debug(f"[{agent_name}] Raw response (first 500 chars): {response[:500]}")
        self.logger.debug(f"[{agent_name}] Raw response (last 200 chars): {response[-200:]}")

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                self.logger.debug(f"[{agent_name}] JSON match found, length: {len(json_str)} chars")
                self.logger.debug(f"[{agent_name}] JSON content (first 300 chars): {json_str[:300]}")

                parsed = json.loads(json_str)
                self.logger.debug(f"[{agent_name}] Successfully parsed JSON with keys: {list(parsed.keys())}")

                parsed['agent_name'] = agent_name
                parsed['raw_response'] = response
                return parsed
            else:
                self.logger.warning(f"[{agent_name}] No JSON pattern found in response")
                self.logger.warning(f"[{agent_name}] Full response for inspection: {response}")
                return {
                    "agent_name": agent_name,
                    "decision": "HOLD",
                    "direction": "NEUTRAL",
                    "confidence": 50,
                    "reasoning": f"{agent_name} parsing failed - no JSON found",
                    "take_profit": 0,
                    "stop_loss": 0,
                    "entry_price": 0,
                    "parse_error": True,
                    "raw_response": response
                }
        except json.JSONDecodeError as e:
            self.logger.error(f"[{agent_name}] JSON decode error: {e}")
            self.logger.error(f"[{agent_name}] Attempted to parse: {json_match.group() if json_match else 'N/A'}")
            return {
                "agent_name": agent_name,
                "decision": "HOLD",
                "direction": "NEUTRAL",
                "confidence": 50,
                "reasoning": f"JSON decode error: {str(e)}",
                "take_profit": 0,
                "stop_loss": 0,
                "entry_price": 0,
                "parse_error": True,
                "raw_response": response
            }
        except Exception as e:
            self.logger.error(f"[{agent_name}] Failed to parse agent response: {e}")
            return {
                "agent_name": agent_name,
                "decision": "HOLD",
                "direction": "NEUTRAL",
                "confidence": 50,
                "reasoning": f"Parse error: {str(e)}",
                "take_profit": 0,
                "stop_loss": 0,
                "entry_price": 0,
                "parse_error": True,
                "raw_response": response
            }

    def _log_debate_summary(
        self,
        aggressive: Dict[str, Any],
        conservative: Dict[str, Any],
        final: Dict[str, Any]
    ) -> None:
        """Log a summary of the debate."""
        self.logger.info("=" * 80)
        self.logger.info("🎭 MULTI-AGENT DEBATE SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"🔴 Aggressive: {aggressive.get('decision')} {aggressive.get('direction')} "
                        f"({aggressive.get('confidence')}%)")
        self.logger.info(f"   Reasoning: {aggressive.get('reasoning', 'N/A')[:100]}")
        self.logger.info("")
        self.logger.info(f"🔵 Conservative: {conservative.get('decision')} {conservative.get('direction')} "
                        f"({conservative.get('confidence')}%)")
        self.logger.info(f"   Reasoning: {conservative.get('reasoning', 'N/A')[:100]}")
        self.logger.info("")
        self.logger.info(f"⚖️ FINAL DECISION: {final.get('decision')} {final.get('direction')} "
                        f"({final.get('confidence')}%)")
        self.logger.info(f"   Verdict: {final.get('verdict', 'N/A')}")
        self.logger.info(f"   Reasoning: {final.get('reasoning', 'N/A')[:150]}")
        self.logger.info(f"   Entry: {final.get('entry_price')} | TP: {final.get('take_profit')} | "
                        f"SL: {final.get('stop_loss')}")
        self.logger.info("=" * 80)
