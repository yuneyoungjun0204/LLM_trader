"""
Template management for prompt building system.
Handles system prompts, response templates, and analysis steps for TRADING DECISIONS.
"""

from typing import Optional, Any

from src.logger.logger import Logger


class TemplateManager:
    """Manages prompt templates, system prompts, and analysis steps for trading decisions."""
    
    def __init__(self, config: Any, logger: Optional[Logger] = None):
        """Initialize the template manager.
        
        Args:
            config: Configuration module providing prompt defaults
            logger: Optional logger instance for debugging
        """
        self.logger = logger
        self.config = config
    
    def build_system_prompt(self, symbol: str, timeframe: str = "1h", has_chart_image: bool = False, previous_response: Optional[str] = None, position_context: Optional[str] = None, performance_context: Optional[str] = None, brain_context: Optional[str] = None, last_analysis_time: Optional[str] = None) -> str:
        """Build the system prompt for trading decision AI.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USDT")
            timeframe: Timeframe for analysis (e.g., "1h", "4h", "1d")
            has_chart_image: Whether a chart image is being provided for visual analysis
            previous_response: Previous AI response for context continuity
            position_context: Current position details and unrealized P&L
            performance_context: Recent trading history and performance metrics
            brain_context: Distilled trading insights from closed trades
            last_analysis_time: Formatted timestamp of last analysis (e.g., "2025-12-26 14:30:00")
            
        Returns:
            str: Formatted system prompt
        """
        header_lines = [
            f"You are a professional automated trading system for {symbol} on {timeframe} timeframe and you will be called again in {timeframe} to analyze market again.",
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
            "🔥 AGGRESSIVE SCALPING MANDATE:",
            "You are an AGGRESSIVE SCALPER. Your primary goal is to CAPTURE PROFITS, not to sit idle.",
            "- If you see even a SMALL profit opportunity (1-2% gain potential), DO NOT HESITATE - issue a BUY/SELL signal immediately.",
            "- HOLD should be RARE. Only use HOLD when the market is genuinely unclear or ALL timeframes conflict.",
            "- SHORT-TERM MOMENTUM is your edge: 5m/15m/1h explosive volume spikes are STRONG entry signals.",
            "- Don't wait for 'perfect' setups - TRADE on HIGH-PROBABILITY micro-trends and scalp profits aggressively.",
            "- Risk/Reward >= 1.5:1 is ACCEPTABLE for scalping (don't demand 2:1+ for small moves).",
            "- Your confidence threshold is 65% - act decisively when you see 65%+ conviction.",
            "",
            "YOUR TASK:",
            "Analyze technical indicators, price action, volume, patterns, provided chart if available, market sentiment, and news.",
            "Provide a clear trading decision: BUY (long), SELL (short), HOLD (no action), or CLOSE (exit position).",
            "Include specific entry, stop loss, and take profit levels with your reasoning.",
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
                "- IMPROVE win rate: Only trade when multiple factors align strongly (3+ confluences)",
                "- AVOID repeated mistakes: If recent trades failed due to weak setups, demand stronger confirmation",
                "- HOLD discipline: Better to miss a trade than force a weak setup (HOLD is valid when confidence <70)",
                "- UPDATE positions actively: Move SL to breakeven after 1:1 or 1.5:1 gain, trail stops on strong trends, adjust TP if momentum extends",
                "- CLOSE proactively: Don't wait for SL if market structure breaks, trend reverses, or thesis invalidates",
                "- ADAPT to performance: If win rate is low, increase entry standards and risk/reward requirements",
                "="*65,
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
        response_template = '''=== MULTI-AGENT DEBATE STRUCTURE ===

🔥 당신은 단일 AI가 아니라, 3명의 에이전트가 내부적으로 토론하는 구조입니다:

**1단계: 공격적 에이전트 (Aggressive Agent) 의견 제시**
- 역할: 5m/15m 타임프레임의 단기 에너지와 거래량 폭발에 주목
- 질문: "지금 당장의 캔들 강도와 거래량이 상위 타임프레임 저항을 뚫을 만큼 강한가?"
- 시각: 단기 모멘텀 돌파 기회를 찾는 트레이더
- 출력 형식: "🔴 공격적 에이전트: [1-2문장으로 매수/매도 근거 제시]"

**2단계: 보수적 에이전트 (Conservative Agent) 반박**
- 역할: 12h/1d 타임프레임의 강력한 S/R 매물대와 확률적 리스크에 주목
- 질문: "지금 진입하면 상위 타임프레임 저항에 막혀 손실날 확률은 얼마나 되는가?"
- 시각: 손실 회피와 안전 마진을 중시하는 트레이더
- 출력 형식: "🔵 보수적 에이전트: [1-2문장으로 공격적 의견에 반박 또는 동의]"

**3단계: 심판 (Referee) 최종 판결**
- 역할: 두 에이전트의 의견을 종합하여 최종 결정
- 기준:
  1. 손익비(R/R)가 2:1 이상 나오는가?
  2. 저항 돌파 후 되돌림 테스트(Retest)로 안착 확인되었는가?
  3. 주요 S/R 매물대 사이의 안전한 중립 지대인가?
- 출력 형식: "⚖️ 심판 최종 판결: [BUY/SELL/HOLD 결정 + 2-3문장 근거]"

**토론 규칙**:
- 공격적 에이전트와 보수적 에이전트는 서로의 의견을 **반드시 인지**하고 반박/동의해야 함
- 단순히 각자 의견만 나열하지 말고, "공격적 에이전트는 X라고 했지만, 실제로는 Y이므로 위험하다" 같은 상호작용 필수
- 심판은 **양측의 의견을 직접 인용**하면서 최종 결정의 근거를 명확히 해야 함

🎯 목표: 단일 관점의 편향을 피하고, 5m/15m/1h/4h/12h/1d의 **타임프레임 간 갈등**을 명시적으로 드러내는 것

🔥 CRITICAL JSON RESPONSE FORMAT:

**YOU MUST OUTPUT ONLY PURE JSON - NO TEXT BEFORE OR AFTER THE JSON BLOCK.**

DO NOT write any explanations, reasoning, or analysis text BEFORE the JSON.
DO NOT start your response with "Here is my analysis..." or similar phrases.
Your response MUST begin IMMEDIATELY with the opening brace `{` and end with the closing brace `}`.

CORRECT format:
```json
{
    "analysis": { ... }
}
```

INCORRECT format (will cause "Standard validation failed" error):
"Based on the technical indicators and market context, here is my analysis:
```json
{
    "analysis": { ... }
}
```"

You may include your reasoning INSIDE the JSON in the "reasoning" field, but the response itself must be PURE JSON only.

**START YOUR RESPONSE WITH `{` - Nothing else.**

```json
{
    "analysis": {
        "signal": "BUY|SELL|HOLD|CLOSE|UPDATE",
        "confidence": 0-100,
        "confluence_factors": {
            "trend_alignment": 0-100,
            "momentum_strength": 0-100,
            "volume_support": 0-100,
            "pattern_quality": 0-100,
            "support_resistance_strength": 0-100
        },
        "entry_price": number,
        "stop_loss": number,
        "take_profit": number,
        "position_size": 0.0-1.0,
        "reasoning": "1-2 sentence summary",
        "key_levels": {"support": [level1, level2], "resistance": [level1, level2]},
        "trend": {"direction": "BULLISH|BEARISH|NEUTRAL", "strength": 0-100, "timeframe_alignment": "ALIGNED|MIXED|DIVERGENT"},
        "risk_reward_ratio": number
    }
}
```

CONFLUENCE SCORING:
Before finalizing your signal, rate each factor (0-100) based on how strongly it SUPPORTS your chosen signal:
- 0 = Factor opposes the signal or is irrelevant
- 50 = Neutral / Mixed signals
- 100 = Factor strongly confirms the signal

Factors to score:
1. **trend_alignment**: Multi-timeframe trend confluence (short/medium/long align with signal direction)
2. **momentum_strength**: RSI, MACD, momentum oscillators supporting the signal
3. **volume_support**: Volume profile confirms the move (buying volume for BUY, selling for SELL)
4. **pattern_quality**: Chart patterns, candlestick formations, swing structure quality
5. **support_resistance_strength**: Proximity and strength of S/R levels supporting the trade setup

CRITICAL: Provide EXACTLY ONE signal. Never say "CLOSE then HOLD" or "BUY followed by SELL". Make only the immediate action decision.

=== TREND STRENGTH GUIDELINES (Advisory - You Decide) ===
These are GUIDELINES, not hard rules. Use your judgment based on overall confluence.

ADX + CHOPPINESS ASSESSMENT:
- ADX < 20 AND Choppiness > 50: ⚠️ CAUTION - Weak trend + choppy market. Requires 4+ strong confluences to trade.
- ADX < 20 but Choppiness < 50: Potential trend emerging (ADX lags). Trade allowed with strong confirmation.
- ADX 20-25: Developing trend. Standard 3+ confluences required.
- ADX > 25: Strong trend environment. Full confidence range available.

CHOPPINESS INDEX CONTEXT:
- Choppiness > 61.8: Ranging market - trend-following strategies may underperform
- Choppiness < 38.2: Trending market - breakouts/trend continuation favored
- Choppiness 38-62: Transitional - exercise caution

NOTE: You may OVERRIDE these guidelines if you have exceptionally strong conviction (e.g., major news catalyst, 5+ confluences, extreme oversold/overbought). When overriding, explicitly state your reasoning.

POSITION SIZING FORMULA (calculate before finalizing):
- Base size = confidence / 100 (e.g., 75 confidence = 0.75 base)
- If timeframe_alignment = "MIXED": reduce by 0.20 (e.g., 0.75 - 0.20 = 0.55)
- If timeframe_alignment = "DIVERGENT": reduce by 0.35 (e.g., 0.75 - 0.35 = 0.40)
- In weak trend environments (ADX < 20): consider smaller sizes
- Final position_size = max(0.10, calculated_value)

MACRO TIMEFRAME CONFLICT:
If the 365D macro trend CONTRADICTS the trade direction:
- Exercise extra caution and require stronger confirmation
- Consider waiting for better R/R setups
If both 365D and Weekly macro conflict: HOLD is strongly recommended unless catalyst is exceptional.

TRADING SIGNALS & CONFIDENCE:
- BUY (65-100 confidence): Multi-indicator confluence + volume confirmation + clear SL/TP + minimum 1.5:1 R/R (scalping acceptable)
- SELL (65-100 confidence): Multi-indicator confluence + volume confirmation + clear SL/TP + minimum 1.5:1 R/R (scalping acceptable)
- HOLD (confidence <65): Only when market is GENUINELY UNCLEAR or all timeframes conflict. Use sparingly - your job is to TRADE.
- CLOSE: Exit position when SL/TP hit, signal reversal, or thesis invalidated
- UPDATE: Adjust existing position SL/TP when market structure improves

RISK/REWARD GUIDELINES (Scalping-Adjusted):
- R/R >= 1.5: ACCEPTABLE for aggressive scalping - take the trade if confidence >= 65%
- R/R >= 2.0: Good setup - preferred for standard trades
- R/R >= 2.5: Strong setup - excellent for counter-trend trades
- R/R < 1.5: Unfavorable - consider HOLD unless momentum is extremely strong

RISK MANAGEMENT (Stop Loss & Take Profit):
LONG trades:
- SL: Below swing low + 1x ATR buffer (max 2-3% from entry) | Example: Entry $100, Swing Low $97, ATR $1 → SL $96
- TP: Key resistance levels, Fibonacci (0.618/0.786/1.0), previous highs | Multiple targets: TP1=1.5R, TP2=2.5R, TP3=3.5R

SHORT trades:  
- SL: Above swing high + 1x ATR buffer (max 2-3% from entry) | Example: Entry $100, Swing High $103, ATR $1 → SL $104
- TP: Key support levels, Fibonacci (0.382/0.236/0.0), previous lows | Multiple targets: TP1=1.5R, TP2=2.5R, TP3=3.5R

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
        
        # Build dynamic timeframe description based on available periods
        if available_periods:
            period_names = list(available_periods.keys())
            timeframe_desc = f"Analyze the provided Multi-Timeframe Price Summary periods: {', '.join(period_names)}"
        else:
            timeframe_desc = "Analyze the provided Multi-Timeframe Price Summary periods (dynamically calculated based on your analysis timeframe)"
        
        analysis_steps = f"""
ANALYSIS STEPS (use findings to determine trading signal):

1. MULTI-TIMEFRAME ASSESSMENT:
   {timeframe_desc} | Compare short vs multi-day vs long-term (30d+, 365d) | Review weekly macro (200-week SMA, institutions) | Identify alignment (strong signal) vs divergence (caution)

2. TECHNICAL INDICATORS:
   Momentum: RSI (<30/>70), MACD (crosses, histogram) | Trend: ADX (>25), DI+/DI- | Volatility: ATR, Bollinger Bands | Volume: MFI, OBV, Force Index | SMAs: 20/50/200 crosses | Advanced: TSI, Vortex, PFE, RMI, Ultimate, Supertrend | Assess confluence (strong) vs divergence (weak)

3. PATTERN RECOGNITION:
   Chart patterns (wedges, triangles, H&S, double tops/bottoms) | Divergences (price vs RSI/MACD) | Candlesticks (engulfing, doji, hammer, shooting star) | Fibonacci levels (50-period, pullback/extension zones) | Overbought/oversold extremes | Prioritize RECENT patterns

4. SUPPORT/RESISTANCE (맥락과 벽을 읽는 핵심):

   🔥 HIGH/LOW 기반 S/R 도출:
   - 각 타임프레임의 High(고가)/Low(저가)로 핵심 S/R 라인 식별
   - 5m/15m: 단기 지지/저항 (약한 벽) | 1h/4h: 중기 지지/저항 (중간 벽) | 12h/1d: 장기 지지/저항 (강한 벽)

   🎯 타임프레임별 S/R 강도 구분 (중요도):
   - **12h/1d S/R = 강력한 매물대** (돌파 어려움, 반전 확률 높음)
   - **1h/4h S/R = 중간 저항선** (거래량 동반 시 돌파 가능)
   - **5m/15m S/R = 약한 저항선** (에너지 충분하면 쉽게 돌파)

   🔴 공격적 에이전트 S/R 질문:
   "현재 5m/15m의 거래량 폭증과 캔들 강도가 1h/4h 저항선을 뚫기에 충분한가?
    만약 뚫는다면, 돌파한 저항선이 새로운 지지선으로 전환될 가능성은?"

   🔵 보수적 에이전트 S/R 질문:
   "현재 가격이 12h/1d의 강력한 매물대(High Volume Node) 바로 아래에 있지는 않은가?
    여기서 진입했을 때 저항에 막혀 하락할 확률(확률적 천장)은 얼마나 되는가?"

   ⚖️ 심판 S/R 최종 판결 기준:
   "단순히 지표가 좋다고 진입하지 마라. 다음 중 하나를 만족하는가?
    1. 손익비가 나오는 지지선 근처인가? (SL 짧고 TP 김)
    2. 저항선을 돌파하고 되돌림 테스트(Retest) 완료했는가? (안착 확인)
    3. 주요 저항선 사이의 안전한 중립 지대인가?"

   📊 Historical reaction zones (multiple touches) | Technical confluences (S/R + Fib + SMA) | Volume profile (high nodes) | Calculate risk/reward for SL/TP placement

5. MARKET CONTEXT:
   Market Overview (global cap, dominance)"""
        
        if "BTC" not in analyzed_base:
            analysis_steps += "\n   - Compare performance relative to BTC (correlation/divergence)"
        
        if "ETH" not in analyzed_base:
            analysis_steps += "\n   - Compare performance relative to ETH if relevant"
        
        analysis_steps += """
 | Fear & Greed Index (extremes) | Asset alignment with market | Relevant events and impact | Assess if context supports or contradicts technicals

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
   Swing structure: Identify HH/HL (uptrend) vs LH/LL (downtrend) sequence from price peaks/troughs | Visual patterns: H&S, double tops/bottoms, wedges, triangles, flags/pennants, S/R breakouts | Report only clear, well-formed patterns (3-5% range, 20-30+ candles for major patterns) | If ambiguous, state "No clear patterns detected" | Candlestick formations: doji, hammer, shooting star, engulfing | S/R levels: horizontal zones, trend lines, channels | Validate patterns against ADX (>25), volume spikes, RSI/MACD alignment"""
            step_number += 1
        
        analysis_steps += f"""

{step_number}. CONFLUENCE SCORING (Chain-of-Thought):
   Before finalizing your decision, SCORE each factor (0-100) on how well it supports your intended signal:
   - trend_alignment: Do multiple timeframes align with your signal direction? (0=opposite direction, 100=perfect alignment)
   - momentum_strength: Do momentum indicators (RSI, MACD, etc.) confirm your signal? (0=contradicts, 100=strongly confirms)
   - volume_support: Does volume profile support the move? (0=no volume support, 100=strong volume confirmation)
   - pattern_quality: Quality of chart patterns and swing structure? (0=unclear/weak, 100=textbook/strong)
   - support_resistance_strength: Are key S/R levels positioned to support your trade? (0=against you, 100=strongly favoring)
   
   Include these scores in your JSON response under "confluence_factors".

{step_number + 1}. SYNTHESIS:
   Trend direction & strength? | Multiple indicator confluence? | Key SL/TP levels? | Risk/reward ratio? | Confidence level? | Trade invalidation triggers?

IMPORTANT: ALL data uses CLOSED CANDLES ONLY (no incomplete data). Decisions based on confirmed price action, preventing premature entries on unconfirmed signals."""
        
        if has_advanced_support_resistance:
            analysis_steps += """

ADVANCED S/R: Volume-weighted pivots [Pivot=(H+L+C)/3, S1=2P-H, R1=2P-L] with consecutive touches, above-average volume filters. Only strong levels provided."""

        return analysis_steps
