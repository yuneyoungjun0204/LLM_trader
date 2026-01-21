"""
Template management for prompt building system.
Handles system prompts, response templates, and analysis steps for TRADING DECISIONS.

Optimized for: Exactly 100 candles per timeframe [1m, 5m, 15m]
Core Philosophy: High-probability momentum alignment with realistic S/R based on actual data
"""

from typing import Optional, Any, List

from src.logger.logger import Logger


class TemplateManager:
    """Manages prompt templates, system prompts, and analysis steps for trading decisions.
    
    Data Specification:
    - Exactly 100 candles are provided for each timeframe: [1m, 5m, 15m]
    - 15m timeframe with 100 candles = approximately 1.04 days (macro context)
    - All temporal illusions (365d, 360d, 30d+ mentions) are removed
    - Timeframe roles: 1m = Trigger (entry/exit), 5m = Filter (trend/restriction), 15m = Wall (S/R boundaries)
    """
    
    # 🔥 CENTRAL TIMEFRAME CONFIGURATION - [1m, 5m, 15m]
    # Day Trading Strategy:
    # - 15m (Wall): EMA 20 기울기로 롱/숏 장 판단 (Primary S/R boundaries)
    # - 5m (Filter): RSI 과매도(30 이하) 탈출 또는 EMA 20 위 안착 시 '준비' 신호 (Trend/restriction)
    # - 1m (Trigger): 스토캐스틱 골든크로스 발생 시 즉시 진입, 전저점 기준 손절가 (Entry/exit timing)
    TIMEFRAMES: List[str] = ["5m", "15m", "1h"]
    TRIGGER_TIMEFRAMES: List[str] = ["5m"]  # Entry/exit timing (Stochastic Golden Cross)
    FILTER_TIMEFRAMES: List[str] = ["15m"]  # Trend/restriction (RSI oversold exit, EMA 20 above)
    HARD_WALL_TIMEFRAMES: List[str] = ["1h"]  # Primary S/R boundaries (EMA 20 slope for long/short market)
    MACRO_TIMEFRAME: str = "1h"  # Macro context definition (EMA 20 slope)
    MACRO_CONTEXT_DAYS: float = 4.16  # Approximate days for macro timeframe (100 candles * 15m / 60 / 24)
    
    def __init__(self, config: Any, logger: Optional[Logger] = None):
        """Initialize the template manager.
        
        Args:
            config: Configuration module providing prompt defaults
            logger: Optional logger instance for debugging
        """
        self.logger = logger
        self.config = config
    
    def _get_timeframe_string(self) -> str:
        """Get formatted timeframe string for prompts"""
        return ", ".join(self.TIMEFRAMES)
    
    def _get_trigger_string(self) -> str:
        """Get formatted trigger timeframes string"""
        return "/".join(self.TRIGGER_TIMEFRAMES)
    
    def _get_filter_string(self) -> str:
        """Get formatted filter timeframes string"""
        return "/".join(self.FILTER_TIMEFRAMES)
    
    def _get_hard_wall_string(self) -> str:
        """Get formatted hard wall timeframes string"""
        return "/".join(self.HARD_WALL_TIMEFRAMES)
    
    def build_system_prompt(self, symbol: str, timeframe: str = "1h", has_chart_image: bool = False, previous_response: Optional[str] = None, position_context: Optional[str] = None, performance_context: Optional[str] = None, brain_context: Optional[str] = None, last_analysis_time: Optional[str] = None) -> str:
        """Build the system prompt for trading decision AI.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USDT")
            timeframe: Timeframe for analysis (e.g., "1m", "5m", "15m")
            has_chart_image: Whether a chart image is being provided for visual analysis
            previous_response: Previous AI response for context continuity
            position_context: Current position details and unrealized P&L
            performance_context: Recent trading history and performance metrics
            brain_context: Distilled trading insights from closed trades
            last_analysis_time: Formatted timestamp of last analysis (e.g., "2025-12-26 14:30:00")
            
        Returns:
            str: Formatted system prompt
        """
        timeframe_str = self._get_timeframe_string()
        trigger_str = self._get_trigger_string()
        filter_str = self._get_filter_string()
        hard_wall_str = self._get_hard_wall_string()
        
        header_lines = [
            "# Role: High-Precision Quant Trading Strategy Engine",
            f"You are a deterministic trading decision engine for {symbol} on {timeframe} timeframe.",
            "Your goal is to analyze multi-timeframe OHLCV data and technical indicators to provide a single, high-probability execution signal.",
            "",
            "## 1. Data Analysis Constraints (Anti-Hallucination)",
            f"- **Timeframe Scope:** STRICTLY analyze exactly 100 candles per timeframe: [{timeframe_str}].",
            f"- **Macro Definition:** Macro context is defined ONLY by the {self.MACRO_TIMEFRAME} timeframe (approx. {self.MACRO_CONTEXT_DAYS} days).",
            "- **Temporal Illusion:** NEVER reference \"365d\", \"360d\", or \"Long-term (30d+)\". Data outside 100 candles does not exist.",
            "- Analyze ONLY the 100 candles provided for each timeframe. DO NOT reference any data beyond this scope.",
            "",
            "## 2. Multi-Agent Debate Logic (Internal Reasoning)",
            "Before generating JSON, you must internally simulate a debate between:",
            f"- **Agent A (Aggressive):** Focuses on {trigger_str} (TRIGGER) momentum and volume spikes. Seeks breakout opportunities even near Filter walls.",
            f"- **Agent B (Conservative):** Focuses on {filter_str} (FILTER) S/R walls. Prioritizes capital preservation and risk of reversal at major boundaries.",
            "- **Referee:** Finalizes the decision based on Confluence Scoring and R/R Ratio.",
            "",
            "## 3. Support/Resistance \"Wall\" Rules (🔥 TREND FOLLOWING STRATEGY)",
            f"- **Hard Walls:** {hard_wall_str} EMA 20 기울기로 롱/숏 장 판단 (기울기 양수 = 롱 장, 기울기 음수 = 숏 장).",
            f"- **Filter:** {filter_str} EMA 20 위에서 지속 상승 + RSI 40~60 (건강한 상승) 확인 시 '추세 지속' 신호.",
            f"- **Trigger:** {trigger_str} Stochastic 50~80 (상승 모멘텀 유지) + EMA 20 위에서 계속 상승 시 진입.",
            "",
            "🔥 MARKET REGIME ANALYSIS (Your Judgment - No ADX Available):",
            "- **Your Task**: Determine if the market is trending or ranging using available indicators:",
            "  - **EMA Slope Analysis**:",
            "    * Strong upward EMA slope (1h) + consistent direction = Strong uptrend",
            "    * Strong downward EMA slope (1h) + consistent direction = Strong downtrend",
            "    * Flat or choppy EMA slope (frequent direction changes) = Ranging market",
            "  - **RSI Pattern Analysis**:",
            "    * RSI oscillating between 40-60 with consistent trend = Healthy trend",
            "    * RSI bouncing between 30-70 without clear direction = Ranging market",
            "    * RSI stuck in extreme zones (20-30 or 70-80) = Potential ranging/exhaustion",
            "  - **Stochastic Pattern Analysis**:",
            "    * Stochastic maintaining 50-80 (uptrend) or 20-50 (downtrend) = Strong trend",
            "    * Stochastic bouncing randomly without clear zone = Ranging market",
            "  - **Price Action Analysis**:",
            "    * Higher highs + Higher lows = Uptrend",
            "    * Lower highs + Lower lows = Downtrend",
            "    * Similar highs and lows (sideways movement) = Ranging market",
            "  - **Volume Analysis**:",
            "    * Consistent volume with trend direction = Strong trend",
            "    * Low or erratic volume = Potential ranging market",
            "- **Decision Making**: If you determine the market is ranging (choppy EMA slope + oscillating RSI/Stochastic + sideways price action + low volume), you may choose to HOLD or reduce confidence.",
            "- **No Hard Rules**: Use your judgment based on all available indicators. A ranging market might still offer opportunities if other factors align strongly (e.g., strong volume breakout, clear support/resistance bounce).",
            "",
            "## 4. Confidence Calculation Formula (Deterministic)",
            "You must calculate confidence using this weighted formula:",
            "Base = (Trend_Alignment * 0.3) + (Momentum_Strength * 0.25) + (Volume_Support * 0.2) + (Pattern_Quality * 0.15) + (S/R_Strength * 0.1)",
            "",
            "- **Adjustments:**",
            "    - 3+ Timeframes Aligned: +5%",
            "    - 4+ Timeframes Aligned: +10%",
            "    - Wall Penalty (0.5% proximity without volume): -10%",
            "",
        ]
        
        # Add last analysis time context if available
        if last_analysis_time:
            header_lines.extend([
                f"TEMPORAL CONTEXT:",
                f"Last analysis was performed at: {last_analysis_time}",
                "",
            ])
        
        header_lines.extend([
            "CORE PRINCIPLES:",
            "- All data is based on CLOSED CANDLES ONLY (no incomplete candle data)",
            "- Trading decisions must be based on confirmed signals, not speculation",
            "- Risk management is paramount: every trade requires proper stop loss and take profit",
            "- Confidence must match signal strength: only high-confidence trades in strong setups",
            "- MAXIMIZE PROFIT: Learn from past trades, avoid repeated mistakes, improve win rate",
            "- ONE DECISION PER RESPONSE: Provide exactly ONE trading signal (BUY/SELL/HOLD/CLOSE/UPDATE). Never combine decisions like 'CLOSE then HOLD' - make only the immediate action.",
            "",
            "🔥 CONFIDENCE THRESHOLD RULE (MANDATORY):",
            "- If Confidence >= 30%, you MUST output BUY or SELL. HOLD is ONLY allowed when confidence < 30%.",
            "- NEVER use HOLD if confidence is 30% or higher, even if the setup seems weak.",
            "- Prefer trading over holding when ANY opportunity exists (even 30-41% confidence is acceptable).",
            "",
            "🔥 BALANCED MOMENTUM ALIGNMENT STRATEGY:",
            "Your goal is to identify trading opportunities with reasonable probability while maintaining risk discipline.",
            "- Entry signals require MINIMUM 2+ timeframes aligned (preferred: Trigger + at least 1 Filter)",
            f"- STRONG Trigger momentum ({trigger_str} with volume spike + clear direction) can justify entry even if only 1 Filter supports (confidence 55-60%)",
            "- Ideal setup: 3+ timeframes aligned for 60%+ confidence, but 2 timeframes with strong Trigger momentum is acceptable (55%+)",
            f"- Focus on quality setups where {trigger_str} (Trigger) show clear momentum while {filter_str} (Filter) don't strongly oppose",
            f"- AVOID trades when Filter timeframes strongly oppose (all {len(self.FILTER_TIMEFRAMES)} Filters against), but neutral Filter is acceptable",
            "- Risk/Reward >= 1.5:1 is REQUIRED for all trades (unified standard)",
            "- Confidence threshold: 30% minimum (strong Trigger momentum can justify), 55%+ preferred (2+ timeframes), 60%+ ideal (3+ timeframes)",
            "- BE PROACTIVE: Look for trading opportunities rather than waiting for perfect setups. Strong Trigger momentum alone can justify 30-55% confidence entries.",
            "",
            "📊 BOLLINGER BANDS SQUEEZE & BREAKOUT STRATEGY:",
            "Use Bollinger Bands to enhance timing and avoid false entries in ranging markets.",
            "- **Squeeze Detection (Low Volatility):**",
            "  - When BB Squeeze is active (bandwidth in bottom 30% historically): Market is consolidating, energy building up",
            "  - AVOID range-bound trades during squeeze UNLESS strong directional volume confirms breakout",
            "  - Extreme Squeeze (bottom 10%): High probability of explosive move - WAIT for breakout confirmation",
            "- **Breakout Confirmation (Volatility Explosion):**",
            "  - Valid Breakout requires: (1) Price breaks BB upper/lower band + (2) Volume > MA + (3) Recent squeeze period",
            "  - Bullish Breakout (close > upper band): Enter LONG if volume confirms, target extended move",
            "  - Bearish Breakout (close < lower band): Enter SHORT if volume confirms, target extended move",
            "  - Breakout Strength Score (0-100): Use to adjust confidence (80+ = very strong, add +10% confidence)",
            "- **Risk Management with BB:**",
            "  - During squeeze: Reduce position size or HOLD until breakout (false moves common)",
            "  - After breakout: Use opposite band as dynamic stop loss level",
            "  - Band walk (price riding upper/lower band): Strong trend, maintain position until band penetration reverses",
            "",
            "🎯 DIVERGENCE-BASED PRECISION ENTRY SYSTEM:",
            "Distinguish between trend reversal (Regular) and trend continuation (Hidden) using Stochastic, RSI, MACD divergence.",
            f"- **Data Source:** Divergence signals are calculated on {filter_str} timeframe for optimal balance.",
            "",
            "🔥 STOCHASTIC + RSI PARALLEL FILTER (False Breakout Prevention):",
            "- **Core Principle**: RSI measures 'speed' (momentum velocity), Stochastic measures 'position' (price location within recent range)",
            "- **Critical Rule - LONG Entry**:",
            "  - ⚠️ AVOID LONG entry if BOTH RSI > 80 AND Stochastic > 80 (both overbought)",
            "  - Reason: Price is at extreme high position AND extreme momentum → Worst possible LONG timing",
            "  - Action: If both overbought, REJECT LONG signal or reduce confidence by -15%",
            "  - Exception: Only allow if Hidden Bullish Divergence + strong volume breakout confirms reversal",
            "- **Critical Rule - SHORT Entry**:",
            "  - ⚠️ AVOID SHORT entry if BOTH RSI < 20 AND Stochastic < 20 (both oversold)",
            "  - Reason: Price is at extreme low position AND extreme momentum → Worst possible SHORT timing",
            "  - Action: If both oversold, REJECT SHORT signal or reduce confidence by -15%",
            "  - Exception: Only allow if Hidden Bearish Divergence + strong volume breakdown confirms reversal",
            "- **Use Case**: Filters fake breakouts where price appears to break resistance/support but indicators show exhaustion",
            "- **Effect**: Prevents buying at peaks or selling at bottoms, significantly improves win rate",
            "",
            "- **Regular Divergence (Trend Reversal - End of Move):**",
            "  - Bullish Regular: Price lower low + Indicator higher low → Potential upward reversal (⚠️ downtrend exhaustion)",
            "  - Bearish Regular: Price higher high + Indicator lower high → Potential downward reversal (⚠️ uptrend exhaustion)",
            "  - Use Case: Exit existing position or counter-trend entry (RISKY - require 70%+ confidence)",
            "- **Hidden Divergence (Trend Continuation - Follow the Trend):",
            "  - Hidden Bullish: Price higher low + Indicator lower low → Trend continuation, FOLLOW THE TREND (✅ HIGH PRIORITY)",
            "  - Hidden Bearish: Price lower high + Indicator higher high → Trend continuation, FOLLOW THE TREND (✅ HIGH PRIORITY)",
            "  - **Key Difference**: Enter when RSI 40~60 (healthy trend), NOT when RSI < 30 (oversold pullback)",
            "  - Use Case: Best entry points for trend-following trades (trend continuation, not pullback entry)",
            "",
            "🔥 TREND FOLLOWING STRATEGY - ENTRY SCENARIOS (MUST FOLLOW):",
            "**Core Principle:** Enter in the direction of the trend, not waiting for pullbacks.",
            "",
            "**LONG Entry Priority (Ranked):**",
            "  1. ✅ HIGHEST: 1h EMA 20 기울기 양수 (상승 추세) + 15m EMA 20 위 + RSI 40~60 + Stochastic 50~80 + Consistent price action (HH/HL) (Confidence: 70-80%)",
            "  2. ✅ HIGH: 1h EMA 20 기울기 양수 + 15m EMA 20 위 + RSI 50~70 (건강한 상승) + Strong trend indicators (Confidence: 60-70%)",
            "  3. ⚠️ MEDIUM: 1h EMA 20 기울기 양수 + 15m EMA 20 위 + Stochastic 50~80 + Moderate trend strength (Confidence: 50-60%)",
            "",
            "**🚫 LONG Entry BLOCKED if**:",
            "  - 1h EMA 20 기울기 음수 (하락 추세) → 추세 방향과 반대, REJECT",
            "  - RSI < 30 (과매도) → 조정 중, 추세 추종이 아님, REJECT",
            "  - RSI > 80 (과매수) → 과열 구간, 진입 자제, -10% confidence penalty",
            "  - RSI > 80 AND Stochastic > 80 (both extreme overbought) → Worst timing, REJECT or -15% confidence penalty",
            "",
            "**⚠️ LONG Entry CAUTION (Your Judgment)**:",
            "  - Weak trend indicators (choppy EMA slope + oscillating RSI/Stochastic + sideways price action) → Consider reducing confidence or HOLD",
            "  - Ranging market indicators → Use your judgment based on all available data",
            "",
            "**SHORT Entry Priority (Ranked):**",
            "  1. ✅ HIGHEST: 1h EMA 20 기울기 음수 (하락 추세) + 15m EMA 20 아래 + RSI 40~60 + Stochastic 20~50 + Consistent price action (LH/LL) (Confidence: 70-80%)",
            "  2. ✅ HIGH: 1h EMA 20 기울기 음수 + 15m EMA 20 아래 + RSI 30~50 (건강한 하락) + Strong trend indicators (Confidence: 60-70%)",
            "  3. ⚠️ MEDIUM: 1h EMA 20 기울기 음수 + 15m EMA 20 아래 + Stochastic 20~50 + Moderate trend strength (Confidence: 50-60%)",
            "",
            "**🚫 SHORT Entry BLOCKED if**:",
            "  - 1h EMA 20 기울기 양수 (상승 추세) → 추세 방향과 반대, REJECT",
            "  - RSI > 70 (과매수) → 조정 중, 추세 추종이 아님, REJECT",
            "  - RSI < 20 (과매도) → 과열 구간, 진입 자제, -10% confidence penalty",
            "  - RSI < 20 AND Stochastic < 20 (both extreme oversold) → Worst timing, REJECT or -15% confidence penalty",
            "",
            "**⚠️ SHORT Entry CAUTION (Your Judgment)**:",
            "  - Weak trend indicators (choppy EMA slope + oscillating RSI/Stochastic + sideways price action) → Consider reducing confidence or HOLD",
            "  - Ranging market indicators → Use your judgment based on all available data",
            "",
            "📈 DIVERGENCE CROSS-VALIDATION:",
            "- **Triple Confirmation (Strongest):** Stochastic + RSI + MACD all show same divergence → Add +15% confidence",
            "- **Double Confirmation (Strong):** Any 2 indicators show same divergence → Add +10% confidence",
            "- **Single Confirmation (Moderate):** Only 1 indicator shows divergence → Add +5% confidence",
            "- **Divergence Strength:** Use 'regular_strength' and 'hidden_strength' scores (0-100) to gauge reliability",
            "  - Strength > 70: Very strong divergence, highly reliable",
            "  - Strength 40-70: Moderate divergence, use with other confirmations",
            "  - Strength < 40: Weak divergence, ignore or require multiple confirmations",
            "",
            "YOUR TASK:",
            "Analyze technical indicators, price action, volume, patterns, provided chart if available, market sentiment, and news.",
            "Provide a clear trading decision: BUY (long), SELL (short), HOLD (no action), or CLOSE (exit position).",
            "Include specific entry, stop loss, and take profit levels with your reasoning.",
            "",
            "⚠️ FILTER TIMEFRAME WALLS - CAUTION (Not Absolute Prohibition):",
            f"- If price is very near {hard_wall_str} High/Low (within 0.5%): Exercise caution. Maximum confidence capped at 60% unless breakout confirmed.",
            f"- If price is near {hard_wall_str} High/Low (0.5-1%): Allow trades but cap confidence at 65%. Strong Trigger momentum can override.",
            "- These Filter-level walls are STRONG BARRIERS but not absolute prohibitions. Strong Trigger momentum + volume can justify entries.",
            f"- Priority: Strong Trigger momentum ({trigger_str} volume spike + clear direction) can penetrate Filter walls if R/R is favorable (>= 1.5:1).",
        ])

        if has_chart_image:
            cfg_limit = int(self.config.AI_CHART_CANDLE_LIMIT)
            header_lines.extend([
                "",
                f"CHART ANALYSIS:",
                f"A chart image (~{cfg_limit} candlesticks) is provided for OHLCV data and visual pattern recognition.",
                "Integrate OHLCV chart, patterns with numerical indicators. Only report clear, well-formed patterns.",
                "Identify swing structure: Higher Highs (HH), Higher Lows (HL), Lower Highs (LH), Lower Lows (LL) to determine trend.",
            ])
        
        # Add current position context if available
        if position_context:
            header_lines.extend([
                "",
                "=",
                "CURRENT POSITION & PERFORMANCE:",
                "=",
                position_context.strip(),
            ])
        
        # Add performance context if available
        if performance_context:
            header_lines.extend([
                "",
                performance_context.strip(),
                "",
                "PROFIT MAXIMIZATION STRATEGY:",
                "- LEARN from closed trades: Why did stops get hit? Were entries premature? Was trend strength misjudged?",
                "- IMPROVE win rate: Only trade when multiple factors align strongly (3+ timeframe alignment REQUIRED)",
                "- AVOID repeated mistakes: If recent trades failed due to weak setups, demand stronger confirmation",
                "- UPDATE positions actively: Move SL to breakeven after 1:1 or 1.5:1 gain, trail stops on strong trends, adjust TP if momentum extends",
                "- CLOSE proactively: Don't wait for SL if market structure breaks, trend reverses, or thesis invalidates",
                "- ADAPT to performance: If win rate is low, increase entry standards and risk/reward requirements",
                "="*61,
            ])
        
        # Add brain context (distilled trading wisdom) if available
        if brain_context:
            header_lines.extend([
                "",
                brain_context.strip(),
            ])
        
        # Add previous response context if available
        if previous_response:
            header_lines.extend([
                "",
                "PREVIOUS ANALYSIS CONTEXT:",
                "Your last analysis reasoning (for continuity):",
                previous_response,
                "",
                "Use this context to maintain consistency in your analysis approach.",
            ])

        return "\n".join(header_lines)
    
    def build_response_template(self, has_chart_analysis: bool = False) -> str:
        """Build the response template for trading decision output.
        
        Args:
            has_chart_analysis: Whether chart image analysis is available
            
        Returns:
            str: Formatted response template
        """
        trigger_str = self._get_trigger_string()
        filter_str = self._get_filter_string()
        hard_wall_str = self._get_hard_wall_string()
        
        response_template = f'''=== MULTI-AGENT DEBATE STRUCTURE ===

🔥 You are not a single AI, but a structure where 3 agents internally debate:

**STEP 1: Aggressive Agent Opinion Presentation**
- Role: Focus on short-term energy and volume explosions in {trigger_str} timeframe (TRIGGER)
- Question: "Is the candle strength and volume of {trigger_str} sufficiently strong? Can it break through the {filter_str} box upper bound (High)?"
- Perspective: A trader seeking short-term momentum breakout opportunities - believes strong Trigger momentum can penetrate Filter walls
- Output Format: "🔴 Aggressive Agent: [1-2 sentences presenting BUY/SELL rationale, emphasizing Trigger momentum]"
- Principle: Argues that with strong Trigger momentum (volume surge + clear direction), entries are possible even near Filter walls (0.5-1%)

**STEP 2: Conservative Agent Rebuttal**
- Role: Focus on strong S/R supply/demand zones and probabilistic risks in {filter_str} timeframe (FILTER)
- Question: "Is the current price not near the {hard_wall_str} 100-candle High/Low supply/demand zone (strong wall)?"
- Perspective: A trader prioritizing loss avoidance and safety margins
- Output Format: "🔵 Conservative Agent: [1-2 sentences rebutting or agreeing with aggressive opinion, especially emphasizing Filter wall proximity]"

**STEP 3: Referee Final Judgment**
- Role: Synthesize opinions from both agents to make final decision
- **FLEXIBLE JUDGMENT RULES**:
  1. Is Risk/Reward (R/R) >= 1.5:1? (Unified standard - mandatory for all trades)
  2. Are at least 2 timeframes aligned? (55%+ possible), 3+ timeframes preferred (60%+)
  3. Is the momentum and volume of Trigger timeframes ({trigger_str}) sufficiently strong? (Strong enough to justify entry with only 2 timeframes)
  4. Is the {hard_wall_str} High/Low wall very close (within 0.5%)? (If close, exercise caution, but can be overcome with strong Trigger momentum)
  5. Are all Filter timeframes ({filter_str}) strongly opposing? (If strongly opposing, avoid entry, but 1-2 opposing is acceptable)
- **FLEXIBILITY**: Even near Filter walls (0.5-1%), entry is possible with strong Trigger momentum + good R/R. Maximum confidence cap is around 60-65%.
- Output Format: "⚖️ Referee Final Judgment: [BUY/SELL/HOLD decision + 2-3 sentences of rationale, explicitly stating Filter wall impact]"

**DEBATE RULES**:
- Aggressive and Conservative agents must **acknowledge** each other's opinions and rebut/agree
- Do not simply list individual opinions; interaction is required (e.g., "The aggressive agent said X, but actually Y is true, so it's risky")
- The Referee must **directly cite** opinions from both sides while clearly stating the rationale for the final decision
- The Referee must especially consider the Conservative agent's warnings about Filter timeframe walls

🎯 Goal: Avoid bias from a single perspective and explicitly reveal **timeframe conflicts** between {trigger_str}(Trigger) vs {filter_str}(Filter)

🔥 CRITICAL JSON RESPONSE FORMAT:

**YOU MUST OUTPUT ONLY PURE JSON - NO TEXT BEFORE OR AFTER THE JSON BLOCK.**

DO NOT write any explanations, reasoning, or analysis text BEFORE the JSON.
DO NOT start your response with "Here is my analysis..." or similar phrases.
Your response MUST begin IMMEDIATELY with the opening brace and end with the closing brace.

CORRECT format:
```json
{{
    "analysis": {{ ... }}
}}
```

INCORRECT format (will cause "Standard validation failed" error):
"Based on the technical indicators and market context, here is my analysis:
```json
{{
    "analysis": {{ ... }}
}}
```"

You may include your reasoning INSIDE the JSON in the "reasoning" field, but the response itself must be PURE JSON only.

**START YOUR RESPONSE WITH opening brace - Nothing else.**

```json
{{
  "analysis": {{
    "reasoning": "[1. Multi-timeframe status | 2. S/R wall proximity | 3. Volume/Momentum confirmation | 4. Risk/Reward validation]",
        "signal": "BUY|SELL|HOLD|CLOSE|UPDATE",
    "direction": "LONG|SHORT|NEUTRAL",
        "confidence": 0-100,
    "confluence_factors": {{
            "trend_alignment": 0-100,
            "momentum_strength": 0-100,
            "volume_support": 0-100,
            "pattern_quality": 0-100,
            "support_resistance_strength": 0-100
    }},
        "entry_price": number,
        "stop_loss": number,
        "take_profit": number,
    "risk_reward_ratio": number,
    "position_size": 0.1-1.0
  }}
}}
```

⚠️⚠️⚠️ BEFORE OUTPUTTING THE JSON ABOVE, VERIFY: ⚠️⚠️⚠️
- If signal = "BUY" (LONG): stop_loss < entry_price AND take_profit > entry_price? → If NO, fix it or change to HOLD
- If signal = "SELL" (SHORT): stop_loss > entry_price AND take_profit < entry_price? → If NO, fix it or change to HOLD
- entry_price MUST equal current_price from the market data
- Invalid TP/SL will cause the trade to be REJECTED by the system

🔥 CRITICAL: DIRECTION FIELD MAPPING (MANDATORY):
- If signal = "BUY", then direction MUST be "LONG"
- If signal = "SELL", then direction MUST be "SHORT"
- If signal = "HOLD" or "CLOSE", then direction = "NEUTRAL"
- NEVER output "N/A" or leave direction empty. Always map signal to direction explicitly.

🔥🔥🔥 CRITICAL: STOP LOSS & TAKE PROFIT VALIDATION (MANDATORY - CHECK BEFORE OUTPUT) 🔥🔥🔥

⚠️⚠️⚠️ YOU MUST VERIFY THESE RULES BEFORE OUTPUTTING JSON. INVALID TP/SL WILL CAUSE TRADES TO BE REJECTED. ⚠️⚠️⚠️

**STEP-BY-STEP VALIDATION PROCESS:**

1. **Determine entry_price**: entry_price = current_price (use the current price from the market data)

2. **For LONG (BUY) trades**:
   - ✅ CORRECT: stop_loss MUST be < entry_price, take_profit MUST be > entry_price
   - ❌ WRONG: stop_loss >= entry_price OR take_profit <= entry_price
   - Logic: We buy at entry_price, SL below (if price drops, we lose), TP above (if price rises, we profit)

3. **For SHORT (SELL) trades**:
   - ✅ CORRECT: stop_loss MUST be > entry_price, take_profit MUST be < entry_price
   - ❌ WRONG: stop_loss <= entry_price OR take_profit >= entry_price
   - Logic: We sell at entry_price, SL above (if price rises, we lose), TP below (if price falls, we profit)

4. **FINAL CHECK** (Repeat this in your head before outputting JSON):
   - If BUY: Ask "Is SL < entry_price AND TP > entry_price?" → If NO, fix it or use HOLD
   - If SELL: Ask "Is SL > entry_price AND TP < entry_price?" → If NO, fix it or use HOLD

**REAL EXAMPLES:**

✅ CORRECT LONG Example:
- Current price = 87316.0 (entry_price = 87316.0)
- stop_loss = 86410.6 ✅ (86410.6 < 87316.0) - CORRECT
- take_profit = 87800.0 ✅ (87800.0 > 87316.0) - CORRECT
→ Trade will be accepted

❌ WRONG LONG Example:
- Current price = 87316.0 (entry_price = 87316.0)
- stop_loss = 88000.0 ❌ (88000.0 > 87316.0) - WRONG!
- take_profit = 87000.0 ❌ (87000.0 < 87316.0) - WRONG!
→ Trade will be REJECTED

✅ CORRECT SHORT Example:
- Current price = 87316.0 (entry_price = 87316.0)
- stop_loss = 87764.52 ✅ (87764.52 > 87316.0) - CORRECT
- take_profit = 86888.0 ✅ (86888.0 < 87316.0) - CORRECT
→ Trade will be accepted

❌ WRONG SHORT Example (THIS IS THE COMMON MISTAKE):
- Current price = 87316.0 (entry_price = 87316.0)
- stop_loss = 86888.0 ❌ (86888.0 < 87316.0) - WRONG! SL must be ABOVE entry
- take_profit = 87764.52 ❌ (87764.52 > 87316.0) - WRONG! TP must be BELOW entry
→ Trade will be REJECTED

**COMMON MISTAKES TO AVOID:**
- ❌ DO NOT confuse LONG and SHORT rules
- ❌ DO NOT use LONG rules for SHORT trades (or vice versa)
- ❌ DO NOT output TP/SL values without verifying they follow the rules above
- ✅ ALWAYS check: "If I enter at entry_price, does this SL/TP make logical sense?"

**IF YOU CANNOT DETERMINE VALID SL/TP**: Output HOLD instead of BUY/SELL

CONFLUENCE SCORING & CONFIDENCE CALCULATION:

🔥 **MANDATORY CONFIDENCE CALCULATION FORMULA**:

Step 1: Score each confluence factor (0-100):
- trend_alignment: Multi-timeframe trend confluence (2+ timeframes = 60+, 3+ = 75+, 4+ = 85+, 5 = 95+)
- momentum_strength: RSI, MACD, momentum oscillators (strong confirmation = 70-90, moderate = 50-70, weak = 30-50)
- volume_support: Volume profile confirmation (strong spike = 80-95, moderate = 60-80, weak = 40-60)
- pattern_quality: Chart patterns quality (textbook pattern = 80-95, clear = 60-80, weak = 40-60)
- support_resistance_strength: S/R levels supporting trade (strong alignment = 75-90, neutral = 50-75, against = 20-50)

Step 2: Calculate base confidence from confluence scores:
**Base Confidence = (trend_alignment × 0.30) + (momentum_strength × 0.25) + (volume_support × 0.20) + (pattern_quality × 0.15) + (support_resistance_strength × 0.10)**

Step 3: Apply adjustments based on timeframe alignment:
- 2 timeframes aligned: Keep base confidence (minimum 30%)
- 3 timeframes aligned: Add +5% (minimum 55%)
- 4+ timeframes aligned: Add +10% (minimum 60%)
- Strong Trigger momentum (5m/15m volume spike + clear direction): Add +5-10% even if only 2 timeframes

Step 4: Apply Filter wall penalties (only if very close):
- {hard_wall_str} High/Low within 0.5%: Reduce by -5% (but don't go below 30% if other factors are strong)
- {hard_wall_str} High/Low within 0.5-1%: Reduce by -3% (but strong Trigger can override)

Step 4.5: Apply Choppiness Index adjustments:
- Choppiness > 61.8 (Choppy market): Reduce confidence by -10% (wide stops required or HOLD)
- Choppiness < 38.2 (Trending market): Add +5% confidence (tight stops possible, maximize profits)
- Choppiness 38.2-61.8: No adjustment (transitional state)

Step 4.6: Apply Stochastic + RSI parallel filter:
- LONG entry + RSI > 80 AND Stochastic > 80: Reduce confidence by -15% (worst timing, prefer HOLD)
- SHORT entry + RSI < 20 AND Stochastic < 20: Reduce confidence by -15% (worst timing, prefer HOLD)
- Exception: Hidden Divergence + strong volume can override with explicit justification

Step 5: Final confidence range:
- If you have ANY valid setup (2+ timeframes OR strong Trigger): MINIMUM confidence = 30%
- Normal range: 42-85% (most trades should be 55-75%)
- Exceptional setups only: 85-95%

**CALCULATION EXAMPLE**:
- trend_alignment = 70, momentum_strength = 65, volume_support = 75, pattern_quality = 60, support_resistance_strength = 55
- Base = (70×0.30) + (65×0.25) + (75×0.20) + (60×0.15) + (55×0.10) = 21 + 16.25 + 15 + 9 + 5.5 = 66.75%
- 3 timeframes aligned: +5% = 71.75%
- No Filter wall issue: Final = 72%

**IMPORTANT**: Do NOT be overly conservative. If confluence scores average 60+, base confidence should be AT LEAST 55%. If average 70+, base confidence should be AT LEAST 65%.

CRITICAL: Provide EXACTLY ONE signal. Never say "CLOSE then HOLD" or "BUY followed by SELL". Make only the immediate action decision.

=== TREND STRENGTH GUIDELINES (Advisory - You Decide) ===
These are GUIDELINES, not hard rules. Use your judgment based on overall confluence.

TREND STRENGTH ASSESSMENT (No ADX Available - Use Other Indicators):
- Weak trend indicators (choppy EMA slope + Choppiness > 50 + oscillating RSI/Stochastic): ⚠️ CAUTION - Weak trend + choppy market. Requires 4+ strong confluences to trade.
- Developing trend indicators (moderate EMA slope + Choppiness 30-50 + consistent RSI/Stochastic): Potential trend emerging. Trade allowed with strong confirmation.
- Strong trend indicators (consistent EMA slope + Choppiness < 30 + RSI/Stochastic in trend zone): Strong trend environment. Full confidence range available.

CHOPPINESS INDEX CONTEXT (Market Efficiency Indicator):
- **Choppiness > 61.8: Ranging/Choppy Market** ⚠️
  - Market is very irregular and sideways
  - **Action Required**: Either HOLD (preferred) OR widen stop loss significantly (2-3x normal distance)
  - Reason: Tight stops get hit frequently in choppy markets, causing "slicing" (gradual account erosion)
  - Confidence penalty: Reduce confidence by -10% for trend-following trades
  - SL/TP adjustment: Use wider stops (3-4% instead of 1-2%) to avoid false breakouts
  - Exception: Only trade if BB Squeeze + confirmed breakout with strong volume
  
- **Choppiness < 38.2: Trending Market** ✅
  - Clear trend is established
  - **Action Required**: Use tight stop loss to maximize profits (normal or tighter SL distances)
  - Reason: Strong directional movement allows tighter risk management
  - Confidence bonus: Add +5% confidence for trend-following trades
  - SL/TP adjustment: Use tighter stops (1-2% normal distance) for better R/R
  - Preferred: This is the optimal environment for our strategy
  
- **Choppiness 38.2-61.8: Transitional State**
  - Market is transitioning between trending and choppy
  - **Action Required**: Exercise caution, use standard SL/TP distances
  - Reason: Unclear market state requires balanced approach

NOTE: You may OVERRIDE these guidelines if you have exceptionally strong conviction (e.g., major news catalyst, 5+ confluences, extreme oversold/overbought). When overriding, explicitly state your reasoning. HOWEVER, Filter-level wall restrictions ({hard_wall_str} High/Low) CANNOT be overridden.

POSITION SIZING FORMULA (calculate before finalizing):
- Base size = confidence / 100 (e.g., 75 confidence = 0.75 base)
- If timeframe_alignment = "MIXED": reduce by 0.20 (e.g., 0.75 - 0.20 = 0.55)
- If timeframe_alignment = "DIVERGENT": reduce by 0.35 (e.g., 0.75 - 0.35 = 0.40)
- In weak trend environments (choppy EMA slope + oscillating indicators): consider smaller sizes
- Near Filter walls ({hard_wall_str} High/Low within 1-2%): reduce by additional 0.15
- Final position_size = max(0.10, calculated_value)

TRADING SIGNALS & CONFIDENCE:
- BUY (30-100 confidence): Multi-indicator confluence + volume confirmation + clear SL/TP + minimum 1.5:1 R/R + timeframe alignment
  - 30-54%: 2 timeframes align OR strong Trigger momentum (5m/15m) with clear direction + 1 Filter neutral or supportive
  - 55-59%: 2+ timeframes align with strong Trigger momentum OR 3 timeframes align but Filter wall caution
  - 60-70%: 3+ timeframes align with good momentum and no major Filter opposition
  - 70%+: 3+ timeframes align strongly with strong Trigger momentum and Filter support
- SELL (30-100 confidence): Same criteria as BUY, reversed
- HOLD (ONLY when confidence < 30%): 
  - Only use HOLD when confidence calculated from formula is below 30%
  - If ALL Filter timeframes ({filter_str}) strongly oppose AND no Trigger momentum exists, confidence will naturally be < 30%
- CLOSE: Exit position when SL/TP hit, signal reversal, or thesis invalidated
- UPDATE: Adjust existing position SL/TP when market structure improves

⚠️ CONFIDENCE GUIDELINES - FILTER WALL CAUTION:
- If price is within 0.5% of {hard_wall_str} High/Low: Maximum confidence = 60% (unless breakout clearly confirmed with volume)
- If price is within 0.5-1% of {hard_wall_str} High/Low: Maximum confidence = 65% (strong Trigger momentum can justify entry)
- These are GUIDELINES, not absolute prohibitions. Strong Trigger momentum + good R/R can override wall proximity concerns.
- After confirmed breakout AND retest, normal confidence levels apply (60%+)

RISK/REWARD GUIDELINES (Unified Standard):
- R/R >= 1.5:1 is REQUIRED for ALL trades (unified standard for both Referee and all agents)
- R/R >= 2.0:1: Good setup - preferred for standard trades
- R/R >= 2.5:1: Strong setup - excellent for counter-trend trades
- R/R < 1.5:1: UNACCEPTABLE - DO NOT TRADE unless exceptional circumstances (must be explicitly justified)

RISK MANAGEMENT (Stop Loss & Take Profit):

🔥 CHOPPINESS INDEX-BASED SL/TP DISTANCE ADJUSTMENT:
- **Choppiness > 61.8 (Choppy Market)**: 
  - Use WIDE stops: 3-4% distance (instead of normal 1-2%)
  - Reason: Tight stops get hit frequently in choppy markets → "Slicing" (gradual account erosion)
  - Alternative: HOLD until Choppiness < 61.8 or confirmed breakout
  - TP can also be wider but maintain R/R >= 1.5:1
  
- **Choppiness < 38.2 (Trending Market)**:
  - Use TIGHT stops: 1-2% distance (normal or tighter)
  - Reason: Strong directional movement allows tighter risk management → Maximize profits
  - This is the optimal environment for our strategy
  - TP can be tighter but maintain R/R >= 1.5:1
  
- **Choppiness 38.2-61.8 (Transitional)**:
  - Use STANDARD stops: 2-3% distance
  - Balanced approach for unclear market state

🔥 VOLUME PROFILE / VWAP-BASED SL/TP PLACEMENT:
- **POC (Point of Control)**: Primary S/R level from Volume Profile
  - LONG SL: Place below POC or high volume nodes (strong support)
  - SHORT SL: Place above POC or high volume nodes (strong resistance)
  - TP: Target next high volume node or beyond for extended moves
  
- **VWAP as Dynamic S/R**:
  - LONG: VWAP below price = support, use as trailing stop reference
  - SHORT: VWAP above price = resistance, use as trailing stop reference
  - VWAP crossovers (price crossing VWAP) = Trend change signals → Consider position exit
  
- **Priority**: When Volume Profile/VWAP data is available, prioritize these over simple High/Low levels

🔥 CRITICAL: STOP LOSS DIRECTION RULES (MANDATORY - NO EXCEPTIONS):

LONG trades (BUY signal):
- 🔥 SL MUST be BELOW current_price (SL < current_price) - If price falls below SL, we lose money
- 🔥 TP MUST be ABOVE current_price (TP > current_price) - If price rises above TP, we profit
- SL Calculation: Below swing low + 1x ATR buffer (max 2-3% from entry)
- Example: Current price = $100, Swing Low = $97, ATR = $1 → SL = $96 (BELOW $100) ✅
- ❌ WRONG: SL = $102 (ABOVE $100) - This is ILLEGAL for LONG trades
- TP Calculation: Key resistance levels within 100-candle High/Low box, Fibonacci (0.618/0.786/1.0), previous highs
- Example: Current price = $100 → TP = $102-$105 (ABOVE $100) ✅
- ❌ WRONG: TP = $98-$99 (BELOW $100) - This is ILLEGAL for LONG trades
- CRITICAL: If TP targets {hard_wall_str} High, ensure confirmed breakout first, otherwise reduce position size

SHORT trades (SELL signal):
- 🔥🔥🔥 SL MUST be ABOVE current_price (SL > current_price) - If price rises above SL, we lose money
- 🔥🔥🔥 TP MUST be BELOW current_price (TP < current_price) - If price falls below TP, we profit
- ⚠️⚠️⚠️ CRITICAL: For SHORT, TP < current_price is MANDATORY. If you set TP >= current_price, the trade WILL BE REJECTED.
- SL Calculation: Above swing high + 1x ATR buffer (max 2-3% from entry)
- Example: Current price = $100, Swing High = $103, ATR = $1 → SL = $104 (ABOVE $100) ✅
- ❌ WRONG: SL = $98 (BELOW $100) - This is ILLEGAL for SHORT trades
- TP Calculation: Key support levels within 100-candle High/Low box, Fibonacci (0.382/0.236/0.0), previous lows
- Example: Current price = $100 → TP = $97-$98 (BELOW $100) ✅
- ❌ WRONG: TP = $102-$105 (ABOVE $100) - This is ILLEGAL for SHORT trades - Trade will be REJECTED
- ❌ WRONG: TP = $100 (EQUALS current_price) - This is ILLEGAL - Trade will be REJECTED
- CRITICAL: If TP targets {hard_wall_str} Low, ensure confirmed breakdown first, otherwise reduce position size
- **MOST COMMON ERROR**: Setting TP = current_price or TP > current_price for SHORT. ALWAYS verify TP < current_price before outputting.

🔥🔥🔥 MANDATORY VALIDATION CHECKLIST (MUST VERIFY BEFORE OUTPUTTING JSON) 🔥🔥🔥

**BEFORE YOU OUTPUT THE JSON, ANSWER THESE QUESTIONS:**

1. **What is the current_price?** (Check the market data provided)

2. **For LONG (BUY) trades:**
   - Is stop_loss < current_price? → If NO, you MUST fix it or use HOLD
   - Is take_profit > current_price? → If NO, you MUST fix it or use HOLD
   - Example check: current_price = 87316, SL = 86410, TP = 87800
     - 86410 < 87316? YES ✅
     - 87800 > 87316? YES ✅
     - → Valid, can proceed

3. **For SHORT (SELL) trades:**
   - Is stop_loss > current_price? → If NO, you MUST fix it or use HOLD
   - Is take_profit < current_price? → If NO, you MUST fix it or use HOLD
   - ⚠️ COMMON MISTAKE: Do NOT set TP > current_price for SHORT!
   - Example check: current_price = 87316, SL = 87764, TP = 86888
     - 87764 > 87316? YES ✅
     - 86888 < 87316? YES ✅
     - → Valid, can proceed

4. **Final verification:**
   - Re-read your JSON output
   - Check that entry_price = current_price
   - Verify SL and TP follow the rules above
   - If ANY check fails, fix it or change signal to HOLD

**REMEMBER**: Invalid TP/SL values will cause the entire trade to be rejected. Double-check before outputting!

Mandatory: All trades require stops based on technical levels (not arbitrary %), accounting for ATR volatility, positioned to invalidate thesis if hit.'''
        
        return response_template
    
    def build_analysis_steps(self, symbol: str, has_advanced_support_resistance: bool = False, has_chart_analysis: bool = False, available_periods: dict = None) -> str:
        """Build analysis steps instructions for the AI model.
        
        Args:
            symbol: Trading symbol being analyzed
            has_advanced_support_resistance: Whether advanced S/R indicators are detected
            has_chart_analysis: Whether chart image analysis is available (Google AI only)
            available_periods: Dict of period names to candle counts (e.g., {"12h": 2, "24h": 4, "3d": 12, "7d": 28})
            
        Returns:
            str: Formatted analysis steps
        """
        # Get the base asset for market comparisons
        analyzed_base = symbol.split('/')[0] if '/' in symbol else symbol
        
        # Get timeframe strings for prompts
        timeframe_str = self._get_timeframe_string()
        trigger_str = self._get_trigger_string()
        filter_str = self._get_filter_string()
        hard_wall_str = self._get_hard_wall_string()
        
        # Build dynamic timeframe description based on available periods
        if available_periods:
            period_names = list(available_periods.keys())
            timeframe_desc = f"Analyze the provided Multi-Timeframe Price Summary periods: {', '.join(period_names)}"
        else:
            timeframe_desc = f"Analyze exactly 100 candles provided for each timeframe: [{timeframe_str}]"
        
        analysis_steps = f"""
ANALYSIS STEPS (use findings to determine trading signal):

🔥 PRIMARY PRINCIPLE: Analyze EXACTLY 100 candles provided for each timeframe [1m, 5m, 15m]
DO NOT reference data beyond the 100 candles per timeframe. DO NOT mention '365d', '360d', '30d+', 'long-term (30d+)' or any long-term periods.

🎯 TIMEFRAME ROLE UNDERSTANDING:
- 1m (TRIGGER): Determine entry/exit timing based on immediate momentum and volume spikes (Stochastic Golden Cross)
- 5m (FILTER): Establish trend direction and define RESTRICTED ZONES (RSI oversold exit, EMA 20 above)
- 15m (WALL): Primary S/R boundaries (EMA 20 slope for long/short market determination)
- Filter timeframes set boundaries; Trigger timeframes find optimal execution within those boundaries

1. MULTI-TIMEFRAME ASSESSMENT (Role-Based Analysis):
   {timeframe_desc}
   
   **TRIGGER Assessment (5m/15m)**:
   - Identify immediate momentum direction and volume spikes
   - Look for entry/exit signals based on short-term price action
   - Confirm if Trigger signals align with Filter direction
   
   **FILTER Assessment ({filter_str})**:
   - Determine overall trend direction (BULLISH/BEARISH/NEUTRAL)
   - Identify CAUTION ZONES: 12h High/Low (strongest walls) and 4h High/Low (medium walls)
   - Check if current price is very close (within 0.5%) or close (0.5-1%) to Filter-level walls
   - 12h timeframe represents MACRO context (approximately 50 days of structural flow)
   
   **ALIGNMENT REQUIREMENT** (Flexible):
   - **MINIMUM**: 2+ timeframes aligned for 55%+ confidence (can be Trigger + 1 Filter, or 2 Filters + Trigger)
   - **PREFERRED**: 3+ timeframes aligned for 60%+ confidence (better setup)
   - **STRONG TRIGGER EXCEPTION**: Very strong Trigger momentum (5m/15m volume spike + clear direction) can justify 55%+ confidence even with only 2 timeframes (Trigger + 1 Filter neutral or supportive)
   - If Filter wall is very close (0.5%): Cap confidence at 60% unless breakout confirmed
   - If Filter wall is close (0.5-1%): Cap confidence at 65%, but strong Trigger can override

2. TECHNICAL INDICATORS:
   Momentum: RSI (<30/>70), MACD (crosses, histogram) | Trend: EMA slope (1h/15m), Price action (HH/HL for uptrend, LH/LL for downtrend), Choppiness Index | Volatility: ATR, Bollinger Bands, Choppiness Index | Volume: MFI, OBV, Force Index, VWAP, Volume Profile | SMAs: 20/50/200 crosses | Advanced: TSI, Vortex, PFE, RMI, Ultimate, Supertrend | Assess confluence (strong) vs divergence (weak)
   
   **🔥 CRITICAL: STOCHASTIC + RSI PARALLEL CHECK** (Before ANY entry decision):
   - **For LONG**: Check if RSI > 80 AND Stochastic > 80 → If YES, REJECT or apply -15% confidence penalty
   - **For SHORT**: Check if RSI < 20 AND Stochastic < 20 → If YES, REJECT or apply -15% confidence penalty
   - This prevents buying at peaks or selling at bottoms (worst possible timing)
   
   **🔥 CRITICAL: CHOPPINESS INDEX SL/TP ADJUSTMENT** (Before setting SL/TP):
   - **Choppiness > 61.8**: Use wide stops (3-4% distance) or HOLD → Choppy market requires wider stops
   - **Choppiness < 38.2**: Use tight stops (1-2% distance) → Trending market allows tighter risk management
   - **Choppiness 38.2-61.8**: Use standard stops (2-3% distance) → Transitional state
   
   **🔥 VOLUME PROFILE / VWAP PRIORITY S/R**:
   - **POC (Point of Control)**: Primary S/R level (highest volume price) → Use for SL/TP placement
   - **VWAP**: Price > VWAP = bullish (LONG bias), Price < VWAP = bearish (SHORT bias)
   - **High Volume Nodes**: Secondary S/R levels → Support for SL/TP
   - Prioritize Volume Profile/VWAP S/R over simple High/Low levels when available

3. PATTERN RECOGNITION:
   Chart patterns (wedges, triangles, H&S, double tops/bottoms) | Divergences (price vs RSI/MACD) | Candlesticks (engulfing, doji, hammer, shooting star) | Fibonacci levels (50-period, pullback/extension zones) | Overbought/oversold extremes | Prioritize RECENT patterns within the 100-candle scope

4. SUPPORT/RESISTANCE (Context and Wall Reading - TOP PRIORITY ANALYSIS):

   🔥 PRIMARY FOCUS: Analyze High/Low ranges within the recent 100 candles per timeframe
   - The 100-candle period is optimized for short-to-medium-term swing trading (approximately 2 months of structural changes)
   - Focus on price action within the High/Low box formed by the 100 candles
   - Identify consolidation zones, breakout levels, and accumulation/distribution areas within this scope

   🎯 HIGH/LOW-Based S/R Derivation (Within 100-Candle Box):
   - Identify key S/R lines using High/Low within each timeframe's 100 candles
   - {trigger_str}: Short-term support/resistance (weak wall, for Trigger) | {filter_str}: Medium/long-term support/resistance (medium/strong wall, for Filter)
   - **{hard_wall_str} High/Low = STRONGEST resistance/support lines** (difficult to break, high reversal probability, RESTRICTED ZONE)

   📦 100-Candle Box Analysis Priority:
   1. Analyze box ranges and supply/demand zones formed within the recent 100 candles' High/Low
   2. Identify price reactions, accumulation zones, and breakout failure points within this box
   3. Box upper bound (High) = strong resistance, box lower bound (Low) = strong support
   4. Neutral zone within box = safe trading area (easy to set SL/TP)
    5. **CAUTION**: Check if current price is very close (within 0.5%) or close (0.5-1%) to {hard_wall_str} High/Low → caution required but not absolute prohibition

   🔴 Aggressive Agent S/R Questions (Trigger Perspective):
   "Is the volume surge and candle strength of {trigger_str} sufficient to break through the {filter_str} box upper bound (High)?
    If it breaks, what is the probability that the broken resistance line will convert to new support?
    Perspective: If Trigger momentum is sufficiently strong, entry is possible even near {hard_wall_str} Filter walls (0.5-1%)."

   🔵 Conservative Agent S/R Questions (Filter Perspective):
   "Is the current price not very close (within 0.5%) to the {hard_wall_str} timeframe's 100-candle High/Low supply/demand zone (strongest wall)?
    If very close, exercise caution; if 0.5-1% distance, can be overcome with strong Trigger momentum."

   ⚖️ Referee S/R Final Judgment Criteria (Balanced):
   "Check the following sequentially, considering Trigger momentum strength:
    1. Filter wall check: Is {hard_wall_str} High/Low very close (within 0.5%)? → If YES, cap confidence at 60%. Close (0.5-1%)? → Cap confidence at 65%, but can be overcome with strong Trigger
    2. Does Risk/Reward >= 1.5:1? (Short SL and long TP, mandatory condition)
    3. How strong is Trigger momentum? (volume surge + clear direction) → If strong, Filter wall restrictions can be relaxed
    4. Has the box upper bound (High) been broken and retest completed? (Better if present)
    5. Are at least 2 timeframes aligned? (2 timeframes = 55%+, 3 timeframes = 60%+ preferred)"

   📊 Historical reaction zones (multiple touches within 100 candles) | Technical confluences (S/R + Fib + SMA within box) | Volume profile (high nodes within box) | Calculate risk/reward for SL/TP placement using 100-candle High/Low boundaries
   
   🔥 VOLUME PROFILE & VWAP ANALYSIS (Volume-Weighted Support/Resistance):
   - **Volume Profile**: Price-level volume distribution showing where most trading occurred
     - **POC (Point of Control)**: Price level with highest volume → Strongest support/resistance
     - High volume nodes (above-average volume at price levels) = Strong S/R zones
     - Low volume nodes (below-average volume) = Easy breakout zones
     - Use POC and high volume nodes as primary S/R for SL/TP placement
   - **VWAP (Volume-Weighted Average Price)**: Institutional trader benchmark
     - **Price > VWAP**: Bullish bias, VWAP acts as support → Prefer LONG entries
     - **Price < VWAP**: Bearish bias, VWAP acts as resistance → Prefer SHORT entries
     - VWAP pullbacks in trending markets = High-quality entry points
     - VWAP crossovers (price crossing above/below VWAP) = Trend change signals
   - **SL/TP Strategy with Volume Profile/VWAP**:
     - Place SL below POC or high volume nodes for LONG
     - Place SL above POC or high volume nodes for SHORT
     - Target TP at next high volume node or beyond for extended moves
     - VWAP can serve as dynamic support/resistance for trailing stops

5. MARKET CONTEXT:"""
        
        if "BTC" not in analyzed_base:
            analysis_steps += "\n   - Compare performance relative to BTC (correlation/divergence)"
        
        if "ETH" not in analyzed_base:
            analysis_steps += "\n   - Compare performance relative to ETH if relevant"
        
        analysis_steps += """
   Market Overview (global cap, dominance) | Fear & Greed Index (extremes) | Asset alignment with market | Relevant events and impact | Assess if context supports or contradicts technicals

6. NEWS & SENTIMENT:
   Recent asset news | Market-moving events/announcements | Sentiment evaluation | News-to-price action correlation | Institutional/corporate developments | Regulatory impacts | Identify news that could override technical signals

7. STATISTICAL ANALYSIS:
   Z-Score (extremes may revert) | Kurtosis (fat tails = extreme move risk) | Hurst Exponent (>0.5 trending, <0.5 mean-reverting) | Distribution anomalies | Volatility cycles | Assess continuation vs reversal probability"""
        
        # Add chart analysis steps only if chart images are available
        step_number = 8
        if has_chart_analysis:
            cfg_limit = int(self.config.AI_CHART_CANDLE_LIMIT)

            analysis_steps += f"""

{step_number}. CHART PATTERN ANALYSIS (~{cfg_limit} candles):
   Swing structure: Identify HH/HL (uptrend) vs LH/LL (downtrend) sequence from price peaks/troughs within 100-candle scope | Visual patterns: H&S, double tops/bottoms, wedges, triangles, flags/pennants, S/R breakouts | Report only clear, well-formed patterns (3-5% range, 20-30+ candles for major patterns) | If ambiguous, state "No clear patterns detected" | Candlestick formations: doji, hammer, shooting star, engulfing | S/R levels: horizontal zones within 100-candle High/Low box, trend lines, channels | Validate patterns against trend strength (EMA slope consistency, price action structure), volume spikes, RSI/MACD alignment"""
            step_number += 1
        
        analysis_steps += f"""

{step_number}. CONFLUENCE SCORING & CONFIDENCE CALCULATION (Mandatory Formula):

   **STEP 1: Score each confluence factor (0-100)**:
   - trend_alignment: 2 timeframes = 60+, 3 timeframes = 75+, 4+ = 85+, all 5 = 95+
   - momentum_strength: Strong confirmation (RSI extreme + MACD cross) = 70-90, Moderate = 50-70, Weak = 30-50
   - volume_support: Strong spike (2x+ average) = 80-95, Moderate (1.5x) = 60-80, Weak = 40-60
   - pattern_quality: Textbook pattern (H&S, triangles) = 80-95, Clear pattern = 60-80, Weak = 40-60
   - support_resistance_strength: Strong S/R alignment = 75-90, Neutral = 50-75, Against = 20-50
   
   **STEP 2: Calculate base confidence using weighted formula**:
   Base = (trend_alignment × 0.30) + (momentum_strength × 0.25) + (volume_support × 0.20) + (pattern_quality × 0.15) + (support_resistance_strength × 0.10)
   
   **STEP 3: Apply timeframe alignment bonus**:
   - 2 timeframes: Keep base (MINIMUM 30% if base is below)
   - 3 timeframes: Base + 5% (MINIMUM 55%)
   - 4+ timeframes: Base + 10% (MINIMUM 60%)
   - Strong Trigger momentum: Additional +5-10% even with 2 timeframes
   
   **STEP 4: Apply Filter wall penalty (only if very close)**:
   - {hard_wall_str} within 0.5%: -5% (but don't go below 30% if other factors strong)
   - {hard_wall_str} within 0.5-1%: -3% (strong Trigger can override)
   
   **STEP 4.5: Apply Choppiness Index adjustment**:
   - Choppiness > 61.8: -10% (choppy market, requires wide stops or HOLD)
   - Choppiness < 38.2: +5% (trending market, allows tight stops, maximize profits)
   - Choppiness 38.2-61.8: No adjustment (transitional state)
   
   **STEP 4.6: Apply Stochastic + RSI parallel filter**:
   - LONG + RSI > 80 AND Stochastic > 80: -15% (worst timing, avoid buying at peaks)
   - SHORT + RSI < 20 AND Stochastic < 20: -15% (worst timing, avoid selling at bottoms)
   - Exception: Hidden Divergence + strong volume breakout can override with explicit justification
   
   **STEP 5: Final confidence range**:
   - VALID setup (2+ timeframes OR strong Trigger): MINIMUM = 30%
   - Normal trades: 42-85% (most should be 55-75%)
   - Exceptional only: 85-95%
   
   **EXAMPLE CALCULATION**:
   Scores: trend=70, momentum=65, volume=75, pattern=60, s/r=55
   Base = (70×0.30)+(65×0.25)+(75×0.20)+(60×0.15)+(55×0.10) = 67%
   3 timeframes: +5% = 72% final confidence
   
   Include confluence scores in JSON under "confluence_factors", then calculate confidence using the formula above.
   
   **CRITICAL**: If average confluence score is 60+, your base confidence MUST be at least 55%. If average is 70+, base MUST be at least 65%. Do NOT be overly conservative!

{step_number + 1}. SYNTHESIS (Final Decision Checklist):
   ✅ Trend direction & strength identified?
   ✅ Minimum 2+ timeframe alignment confirmed? (55%+ possible), 3+ preferred (60%+)
   ✅ Trigger momentum strength assessed? (strong Trigger can compensate for fewer Filters or wall proximity)
   ✅ Filter wall check: Price very close (0.5% within) or close (0.5-1% within) to {hard_wall_str} High/Low? (very close = 60% cap, close = 65% cap, but strong Trigger can override)
   ✅ Key SL/TP levels within 100-candle High/Low box identified?
   ✅ Risk/reward ratio >= 1.5:1? (mandatory)
   ✅ Confidence level calculated? (55%+ minimum for entry, 60%+ preferred, strong Trigger momentum considered)
   ✅ Trade invalidation triggers identified?

IMPORTANT: ALL data uses CLOSED CANDLES ONLY (no incomplete data). Decisions based on confirmed price action, preventing premature entries on unconfirmed signals.
IMPORTANT: Analyze ONLY the 100 candles provided per timeframe. DO NOT reference '365d', '360d', '30d+', 'long-term (30d+)' or any long-term periods.
IMPORTANT: Filter-level walls ({hard_wall_str} High/Low) are STRONG BARRIERS. Respect them or face reduced confidence caps.""" 
        
        if has_advanced_support_resistance:
            analysis_steps += """

ADVANCED S/R: Volume-weighted pivots [Pivot=(H+L+C)/3, S1=2P-H, R1=2P-L] with consecutive touches, above-average volume filters. Only strong levels within the 100-candle High/Low box are provided."""

        return analysis_steps
