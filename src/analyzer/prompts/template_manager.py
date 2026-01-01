"""
Template management for prompt building system.
Handles system prompts, response templates, and analysis steps for TRADING DECISIONS.

Optimized for: Exactly 100 candles per timeframe [5m, 15m, 1h, 4h, 12h]
Core Philosophy: High-probability momentum alignment with realistic S/R based on actual data
"""

from typing import Optional, Any

from src.logger.logger import Logger


class TemplateManager:
    """Manages prompt templates, system prompts, and analysis steps for trading decisions.
    
    Data Specification:
    - Exactly 100 candles are provided for each timeframe: [5m, 15m, 1h, 4h, 12h]
    - 12h timeframe with 100 candles = approximately 50 days (macro context)
    - All temporal illusions (365d, 360d, 30d+ mentions) are removed
    - Timeframe roles: 5m/15m = Trigger (entry/exit), 1h/4h/12h = Filter (trend/restriction)
    """
    
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
            timeframe: Timeframe for analysis (e.g., "5m", "1h", "4h")
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
            "🔥 DATA SPECIFICATION - CRITICAL:",
            "You are provided with EXACTLY 100 candles for each timeframe: [5m, 15m, 1h, 4h, 12h]",
            "- Analyze ONLY the 100 candles provided for each timeframe. DO NOT reference any data beyond this scope.",
            "- DO NOT mention '365d', '360d', '30d+', 'long-term (30d+)' or any long-term periods. These temporal references are ILLUSIONS and do not exist in this system.",
            "- Your analysis scope is strictly limited to the recent 100 candles per timeframe (approximately 2 months of structural changes).",
            "- PRIMARY PRINCIPLE: Analyze exactly the 100 candles provided for each timeframe.",
            "",
            "🎯 TIMEFRAME ROLE DEFINITION:",
            "- 5m/15m: TRIGGER role - Determine entry and exit timing based on immediate momentum and volume spikes",
            "- 1h/4h/12h: FILTER role - Establish trend direction and define RESTRICTED ZONES (where entries are prohibited)",
            "- The Filter timeframes set the boundaries; Trigger timeframes find optimal execution within those boundaries",
            "",
            "🔥 MACRO CONTEXT DEFINITION:",
            "- In this system, 'MACRO CONTEXT' refers exclusively to the 12h timeframe with 100 candles (approximately 50 days)",
            "- 12h High/Low levels are the STRONGEST resistance/support zones (hard walls)",
            "- 4h High/Low levels are also strong barriers (medium walls)",
            "- Focus on structural changes within the recent 2-month period, not year-long trends",
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
            "🔥 BALANCED MOMENTUM ALIGNMENT STRATEGY:",
            "Your goal is to identify trading opportunities with reasonable probability while maintaining risk discipline.",
            "- Entry signals require MINIMUM 2+ timeframes aligned (preferred: Trigger + at least 1 Filter)",
            "- STRONG Trigger momentum (5m/15m with volume spike + clear direction) can justify entry even if only 1 Filter supports (confidence 55-60%)",
            "- Ideal setup: 3+ timeframes aligned for 60%+ confidence, but 2 timeframes with strong Trigger momentum is acceptable (55%+)",
            "- Focus on quality setups where 5m/15m (Trigger) show clear momentum while 1h/4h/12h (Filter) don't strongly oppose",
            "- AVOID trades when Filter timeframes strongly oppose (all 3 Filters against), but neutral Filter is acceptable",
            "- Risk/Reward >= 1.5:1 is REQUIRED for all trades (unified standard)",
            "- Confidence threshold: 30% minimum (strong Trigger momentum can justify), 55%+ preferred (2+ timeframes), 60%+ ideal (3+ timeframes)",
            "- BE PROACTIVE: Look for trading opportunities rather than waiting for perfect setups. Strong Trigger momentum alone can justify 30-55% confidence entries.",
            "",
            "YOUR TASK:",
            "Analyze technical indicators, price action, volume, patterns, provided chart if available, market sentiment, and news.",
            "Provide a clear trading decision: BUY (long), SELL (short), HOLD (no action), or CLOSE (exit position).",
            "Include specific entry, stop loss, and take profit levels with your reasoning.",
            "",
            "⚠️ FILTER TIMEFRAME WALLS - CAUTION (Not Absolute Prohibition):",
            "- If price is very near 12h High/Low (within 0.5%): Exercise caution. Maximum confidence capped at 60% unless breakout confirmed.",
            "- If price is near 12h High/Low (0.5-1%): Allow trades but cap confidence at 65%. Strong Trigger momentum can override.",
            "- If price is near 4h High/Low (within 0.5%): Exercise caution. Maximum confidence capped at 60% unless breakout confirmed.",
            "- These Filter-level walls are STRONG BARRIERS but not absolute prohibitions. Strong Trigger momentum + volume can justify entries.",
            "- Priority: Strong Trigger momentum (5m/15m volume spike + clear direction) can penetrate Filter walls if R/R is favorable (>= 1.5:1).",
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
                "- HOLD discipline: ONLY use HOLD when confidence < 30% (calculated from formula). If confidence >= 30%, you MUST choose BUY or SELL. NEVER use 40% for HOLD. Prefer trading over holding when ANY opportunity exists.",
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
        response_template = '''=== MULTI-AGENT DEBATE STRUCTURE ===

🔥 당신은 단일 AI가 아니라, 3명의 에이전트가 내부적으로 토론하는 구조입니다:

**1단계: 공격적 에이전트 (Aggressive Agent) 의견 제시**
- 역할: 5m/15m 타임프레임(TRIGGER)의 단기 에너지와 거래량 폭발에 주목
- 질문: "5m/15m의 캔들 강도와 거래량이 충분히 강한가? 이것이 1h/4h 박스권 상단(High)을 뚫을 수 있는가?"
- 시각: 단기 모멘텀 돌파 기회를 찾는 트레이더 - 강한 Trigger 모멘텀은 Filter 벽도 뚫을 수 있다고 믿음
- 출력 형식: "🔴 공격적 에이전트: [1-2문장으로 매수/매도 근거 제시, Trigger 모멘텀 강조]"
- 원칙: 강한 Trigger 모멘텀(거래량 폭증 + 명확한 방향)이 있으면 Filter 벽 근처(0.5-1%)에서도 진입 가능하다고 주장

**2단계: 보수적 에이전트 (Conservative Agent) 반박**
- 역할: 12h/4h 타임프레임(FILTER)의 강력한 S/R 매물대와 확률적 리스크에 주목
- 질문: "현재 가격이 12h/4h의 100캔들 High/Low 매물대(강력한 벽) 근처에 있지 않은가?"
- 시각: 손실 회피와 안전 마진을 중시하는 트레이더
- 출력 형식: "🔵 보수적 에이전트: [1-2문장으로 공격적 의견에 반박 또는 동의, 특히 Filter 벽 근접성 강조]"

**3단계: 심판 (Referee) 최종 판결**
- 역할: 두 에이전트의 의견을 종합하여 최종 결정
- **FLEXIBLE JUDGMENT RULES**:
  1. 손익비(R/R)가 1.5:1 이상 나오는가? (통일된 기준 - 모든 거래에 필수)
  2. 최소 2개 타임프레임이 정렬되어 있는가? (55%+ 가능), 3개 이상이면 60%+ (선호)
  3. Trigger 타임프레임(5m/15m)의 모멘텀과 거래량이 충분히 강한가? (강하면 2개 타임프레임만으로도 진입 가능)
  4. 12h/4h High/Low 벽이 매우 가까운가(0.5% 이내)? (가까우면 주의, 하지만 강한 Trigger 모멘텀으로 극복 가능)
  5. 모든 Filter 타임프레임(1h/4h/12h)이 강하게 반대하는가? (강하게 반대면 진입 자제, 하지만 1-2개만 반대면 허용)
- **FLEXIBILITY**: Filter 벽 근처(0.5-1%)에서도 강한 Trigger 모멘텀 + 좋은 R/R이면 진입 가능. 최대 신뢰도 제한은 60-65% 정도.
- 출력 형식: "⚖️ 심판 최종 판결: [BUY/SELL/HOLD 결정 + 2-3문장 근거, Filter 벽 영향 명시]"

**토론 규칙**:
- 공격적 에이전트와 보수적 에이전트는 서로의 의견을 **반드시 인지**하고 반박/동의해야 함
- 단순히 각자 의견만 나열하지 말고, "공격적 에이전트는 X라고 했지만, 실제로는 Y이므로 위험하다" 같은 상호작용 필수
- 심판은 **양측의 의견을 직접 인용**하면서 최종 결정의 근거를 명확히 해야 함
- 심판은 특히 Filter 타임프레임의 벽에 대한 보수적 에이전트의 경고를 반드시 고려해야 함

🎯 목표: 단일 관점의 편향을 피하고, 5m/15m(Trigger) vs 1h/4h/12h(Filter)의 **타임프레임 간 갈등**을 명시적으로 드러내는 것

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
        "direction": "LONG|SHORT|NEUTRAL",
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

🔥 CRITICAL: DIRECTION FIELD MAPPING (MANDATORY):
- If signal = "BUY", then direction MUST be "LONG"
- If signal = "SELL", then direction MUST be "SHORT"
- If signal = "HOLD" or "CLOSE", then direction = "NEUTRAL"
- NEVER output "N/A" or leave direction empty. Always map signal to direction explicitly.

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
- 12h/4h High/Low within 0.5%: Reduce by -5% (but don't go below 30% if other factors are strong)
- 12h/4h High/Low within 0.5-1%: Reduce by -3% (but strong Trigger can override)

Step 5: Final confidence range:
- If you have ANY valid setup (2+ timeframes OR strong Trigger): MINIMUM confidence = 30% (NOT 40%!)
- If confidence >= 30%, you MUST choose BUY or SELL (NOT HOLD)
- Normal range: 42-85% (most trades should be 55-75%)
- Exceptional setups only: 85-95%
- HOLD is ONLY allowed when confidence < 30% (calculate using formula, do not arbitrarily use 40%)
- ⚠️ NEVER use 40% for HOLD - if confidence is 40%, you MUST choose BUY or SELL

**CALCULATION EXAMPLE**:
- trend_alignment = 70, momentum_strength = 65, volume_support = 75, pattern_quality = 60, support_resistance_strength = 55
- Base = (70×0.30) + (65×0.25) + (75×0.20) + (60×0.15) + (55×0.10) = 21 + 16.25 + 15 + 9 + 5.5 = 66.75%
- 3 timeframes aligned: +5% = 71.75%
- No Filter wall issue: Final = 72%

**IMPORTANT**: Do NOT be overly conservative. If confluence scores average 60+, base confidence should be AT LEAST 55%. If average 70+, base confidence should be AT LEAST 65%.

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

NOTE: You may OVERRIDE these guidelines if you have exceptionally strong conviction (e.g., major news catalyst, 5+ confluences, extreme oversold/overbought). When overriding, explicitly state your reasoning. HOWEVER, Filter-level wall restrictions (4h/12h High/Low) CANNOT be overridden.

POSITION SIZING FORMULA (calculate before finalizing):
- Base size = confidence / 100 (e.g., 75 confidence = 0.75 base)
- If timeframe_alignment = "MIXED": reduce by 0.20 (e.g., 0.75 - 0.20 = 0.55)
- If timeframe_alignment = "DIVERGENT": reduce by 0.35 (e.g., 0.75 - 0.35 = 0.40)
- In weak trend environments (ADX < 20): consider smaller sizes
- Near Filter walls (4h/12h High/Low within 1-2%): reduce by additional 0.15
- Final position_size = max(0.10, calculated_value)

TRADING SIGNALS & CONFIDENCE:
- BUY (30-100 confidence): Multi-indicator confluence + volume confirmation + clear SL/TP + minimum 1.5:1 R/R + timeframe alignment
  - 30-54%: 2 timeframes align OR strong Trigger momentum (5m/15m) with clear direction + 1 Filter neutral or supportive
  - 55-59%: 2+ timeframes align with strong Trigger momentum OR 3 timeframes align but Filter wall caution
  - 60-70%: 3+ timeframes align with good momentum and no major Filter opposition
  - 70%+: 3+ timeframes align strongly with strong Trigger momentum and Filter support
- SELL (30-100 confidence): Same criteria as BUY, reversed
- HOLD (ONLY when confidence < 30% OR all 3 Filters strongly oppose AND no Trigger momentum exists): 
  - ⚠️ CRITICAL: Do NOT use HOLD if you calculate confidence >= 30% based on the formula above
  - ⚠️ CRITICAL: If confidence is 30-41%, you MUST choose either BUY or SELL (even if weak setup)
  - Only use HOLD when: (1) confidence < 30% OR (2) ALL 3 Filter timeframes (1h/4h/12h) strongly oppose AND no Trigger momentum exists
  - If HOLD is chosen, confidence MUST be below 30% (not 40% or any other value)
  - Prefer trading over holding when ANY opportunity exists (even 30-41% confidence is acceptable)
- CLOSE: Exit position when SL/TP hit, signal reversal, or thesis invalidated
- UPDATE: Adjust existing position SL/TP when market structure improves

⚠️ CONFIDENCE GUIDELINES - FILTER WALL CAUTION:
- If price is within 0.5% of 12h High/Low: Maximum confidence = 60% (unless breakout clearly confirmed with volume)
- If price is within 0.5-1% of 12h High/Low: Maximum confidence = 65% (strong Trigger momentum can justify entry)
- If price is within 0.5% of 4h High/Low: Maximum confidence = 60% (unless breakout clearly confirmed)
- These are GUIDELINES, not absolute prohibitions. Strong Trigger momentum + good R/R can override wall proximity concerns.
- After confirmed breakout AND retest, normal confidence levels apply (60%+)

RISK/REWARD GUIDELINES (Unified Standard):
- R/R >= 1.5:1 is REQUIRED for ALL trades (unified standard for both Referee and all agents)
- R/R >= 2.0:1: Good setup - preferred for standard trades
- R/R >= 2.5:1: Strong setup - excellent for counter-trend trades
- R/R < 1.5:1: UNACCEPTABLE - DO NOT TRADE unless exceptional circumstances (must be explicitly justified)

RISK MANAGEMENT (Stop Loss & Take Profit):
LONG trades:
- SL: Below swing low + 1x ATR buffer (max 2-3% from entry) | Example: Entry $100, Swing Low $97, ATR $1 → SL $96
- TP: Key resistance levels within 100-candle High/Low box, Fibonacci (0.618/0.786/1.0), previous highs | Multiple targets: TP1=1.5R, TP2=2.5R, TP3=3.5R
- CRITICAL: If TP targets 12h/4h High, ensure confirmed breakout first, otherwise reduce position size

SHORT trades:  
- SL: Above swing high + 1x ATR buffer (max 2-3% from entry) | Example: Entry $100, Swing High $103, ATR $1 → SL $104
- TP: Key support levels within 100-candle High/Low box, Fibonacci (0.382/0.236/0.0), previous lows | Multiple targets: TP1=1.5R, TP2=2.5R, TP3=3.5R
- CRITICAL: If TP targets 12h/4h Low, ensure confirmed breakdown first, otherwise reduce position size

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
            timeframe_desc = "Analyze exactly 100 candles provided for each timeframe: [5m, 15m, 1h, 4h, 12h]"
        
        analysis_steps = f"""
ANALYSIS STEPS (use findings to determine trading signal):

🔥 PRIMARY PRINCIPLE: Analyze EXACTLY 100 candles provided for each timeframe [5m, 15m, 1h, 4h, 12h]
DO NOT reference data beyond the 100 candles per timeframe. DO NOT mention '365d', '360d', '30d+', 'long-term (30d+)' or any long-term periods.

🎯 TIMEFRAME ROLE UNDERSTANDING:
- 5m/15m (TRIGGER): Determine entry/exit timing based on immediate momentum and volume spikes
- 1h/4h/12h (FILTER): Establish trend direction and define RESTRICTED ZONES (prohibited entry areas)
- Filter timeframes set boundaries; Trigger timeframes find optimal execution within those boundaries

1. MULTI-TIMEFRAME ASSESSMENT (Role-Based Analysis):
   {timeframe_desc}
   
   **TRIGGER Assessment (5m/15m)**:
   - Identify immediate momentum direction and volume spikes
   - Look for entry/exit signals based on short-term price action
   - Confirm if Trigger signals align with Filter direction
   
   **FILTER Assessment (1h/4h/12h)**:
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
   Momentum: RSI (<30/>70), MACD (crosses, histogram) | Trend: ADX (>25), DI+/DI- | Volatility: ATR, Bollinger Bands | Volume: MFI, OBV, Force Index | SMAs: 20/50/200 crosses | Advanced: TSI, Vortex, PFE, RMI, Ultimate, Supertrend | Assess confluence (strong) vs divergence (weak)

3. PATTERN RECOGNITION:
   Chart patterns (wedges, triangles, H&S, double tops/bottoms) | Divergences (price vs RSI/MACD) | Candlesticks (engulfing, doji, hammer, shooting star) | Fibonacci levels (50-period, pullback/extension zones) | Overbought/oversold extremes | Prioritize RECENT patterns within the 100-candle scope

4. SUPPORT/RESISTANCE (맥락과 벽을 읽는 핵심 - 최우선 분석):

   🔥 PRIMARY FOCUS: Analyze High/Low ranges within the recent 100 candles per timeframe
   - The 100-candle period is optimized for short-to-medium-term swing trading (approximately 2 months of structural changes)
   - Focus on price action within the High/Low box formed by the 100 candles
   - Identify consolidation zones, breakout levels, and accumulation/distribution areas within this scope

   🎯 HIGH/LOW 기반 S/R 도출 (100캔들 박스권 내):
   - 각 타임프레임의 100캔들 내 High(고가)/Low(저가)로 핵심 S/R 라인 식별
   - 5m/15m: 단기 지지/저항 (약한 벽, Trigger용) | 1h: 중기 지지/저항 (중간 벽, Filter용) | 4h/12h: 장기 지지/저항 (강한 벽, Filter용)
   - **12h High/Low = 가장 강력한 저항/지지선** (돌파 어려움, 반전 확률 높음, RESTRICTED ZONE)
   - **4h High/Low = 강한 저항/지지선** (돌파 어려움, RESTRICTED ZONE)

   📦 100캔들 박스권 분석 우선순위:
   1. 최근 100캔들의 High(고가)와 Low(저가) 내에서 형성된 박스권과 매물대 분석
   2. 이 박스권 내에서의 가격 반응, 집적 구간, 돌파 실패 지점 식별
   3. 박스권 상단(High) = 강력한 저항, 박스권 하단(Low) = 강력한 지지
   4. 박스권 내 중립 지대 = 안전한 거래 구간 (SL/TP 설정 용이)
    5. **CAUTION**: 현재 가격이 12h High/Low 또는 4h High/Low 매우 가까이(0.5% 이내) 또는 가까이(0.5-1%)인지 확인 → 주의 필요하지만 절대 금지는 아님

   🔴 공격적 에이전트 S/R 질문 (Trigger 관점):
   "5m/15m의 거래량 폭증과 캔들 강도가 1h/4h 박스권 상단(High)을 뚫기에 충분한가?
    만약 뚫는다면, 돌파한 저항선이 새로운 지지선으로 전환될 가능성은?
    Trigger 모멘텀이 충분히 강하면 12h/4h Filter 벽 근처(0.5-1%)에서도 진입 가능하다는 관점."

   🔵 보수적 에이전트 S/R 질문 (Filter 관점):
   "현재 가격이 12h 타임프레임의 100캔들 High/Low 매물대(가장 강력한 벽) 매우 가까이(0.5% 이내)에 있지는 않은가?
    현재 가격이 4h 타임프레임의 100캔들 High/Low 매물대(강한 벽) 매우 가까이(0.5% 이내)에 있지는 않은가?
    매우 가까우면 주의하되, 0.5-1% 거리라면 강한 Trigger 모멘텀으로 극복 가능."

   ⚖️ 심판 S/R 최종 판결 기준 (균형적):
   "다음을 순차적으로 확인하되, Trigger 모멘텀의 강도를 고려:
    1. Filter 벽 확인: 12h/4h High/Low 매우 가까움(0.5% 이내)? → YES면 신뢰도 60% 제한. 가까움(0.5-1%)? → 신뢰도 65% 제한, 하지만 강한 Trigger로 극복 가능
    2. 손익비 1.5:1 이상이 나오는가? (SL 짧고 TP 김, 필수 조건)
    3. Trigger 모멘텀이 얼마나 강한가? (거래량 폭증 + 명확한 방향) → 강하면 Filter 벽 완화 가능
    4. 박스권 상단(High)을 돌파하고 되돌림 테스트(Retest) 완료했는가? (있으면 더 좋음)
    5. 최소 2개 타임프레임이 정렬되어 있는가? (2개면 55%+, 3개면 60%+ 선호)"

   📊 Historical reaction zones (multiple touches within 100 candles) | Technical confluences (S/R + Fib + SMA within box) | Volume profile (high nodes within box) | Calculate risk/reward for SL/TP placement using 100-candle High/Low boundaries

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
   Swing structure: Identify HH/HL (uptrend) vs LH/LL (downtrend) sequence from price peaks/troughs within 100-candle scope | Visual patterns: H&S, double tops/bottoms, wedges, triangles, flags/pennants, S/R breakouts | Report only clear, well-formed patterns (3-5% range, 20-30+ candles for major patterns) | If ambiguous, state "No clear patterns detected" | Candlestick formations: doji, hammer, shooting star, engulfing | S/R levels: horizontal zones within 100-candle High/Low box, trend lines, channels | Validate patterns against ADX (>25), volume spikes, RSI/MACD alignment"""
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
   - 12h/4h within 0.5%: -5% (but don't go below 30% if other factors strong)
   - 12h/4h within 0.5-1%: -3% (strong Trigger can override)
   
   **STEP 5: Final confidence range**:
   - VALID setup (2+ timeframes OR strong Trigger): MINIMUM = 30%
   - If confidence >= 30%, you MUST choose BUY or SELL (NOT HOLD)
   - Normal trades: 42-85% (most should be 55-75%)
   - Exceptional only: 85-95%
   - HOLD is ONLY allowed when confidence < 30% (calculated from formula)
   - ⚠️ NEVER use 40% for HOLD - if confidence is 40%, you MUST choose BUY or SELL
   
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
   ✅ Filter wall check: Price very close (0.5% within) or close (0.5-1% within) to 12h/4h High/Low? (very close = 60% cap, close = 65% cap, but strong Trigger can override)
   ✅ Key SL/TP levels within 100-candle High/Low box identified?
   ✅ Risk/reward ratio >= 1.5:1? (mandatory)
   ✅ Confidence level calculated? (55%+ minimum for entry, 60%+ preferred, strong Trigger momentum considered)
   ✅ Trade invalidation triggers identified?

IMPORTANT: ALL data uses CLOSED CANDLES ONLY (no incomplete data). Decisions based on confirmed price action, preventing premature entries on unconfirmed signals.
IMPORTANT: Analyze ONLY the 100 candles provided per timeframe. DO NOT reference '365d', '360d', '30d+', 'long-term (30d+)' or any long-term periods.
IMPORTANT: Filter-level walls (4h/12h High/Low) are STRONG BARRIERS. Respect them or face reduced confidence caps."""
        
        if has_advanced_support_resistance:
            analysis_steps += """

ADVANCED S/R: Volume-weighted pivots [Pivot=(H+L+C)/3, S1=2P-H, R1=2P-L] with consecutive touches, above-average volume filters. Only strong levels within the 100-candle High/Low box are provided."""

        return analysis_steps
