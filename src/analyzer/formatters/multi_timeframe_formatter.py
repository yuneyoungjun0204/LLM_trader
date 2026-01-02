"""
Multi-Timeframe Analysis Formatter
Formats multi-timeframe data for AI prompt context
"""
from typing import Dict, Any, List, Optional
import numpy as np


class MultiTimeframeFormatter:
    """Format multi-timeframe analysis data for AI consumption"""

    @staticmethod
    def format_multi_timeframe_summary(mtf_data: Dict[str, Any], symbol: str) -> str:
        """
        Format multi-timeframe data into a comprehensive summary.

        Args:
            mtf_data: Dictionary with timeframe keys (e.g., '5m', '15m', '1h', '4h', '12h')
                     Each contains (ohlcv_array, close_series) tuple
            symbol: Trading pair symbol

        Returns:
            Formatted multi-timeframe summary string
        """
        if not mtf_data:
            return ""

        lines = [
            "=" * 90,
            f"📊 MULTI-TIMEFRAME ANALYSIS - {symbol}",
            "=" * 90,
            ""
        ]

        # Sort timeframes by duration (5m, 15m, 1h, 4h, 12h, 1d)
        timeframe_order = ['5m', '15m', '1h', '4h', '12h', '1d', '1w']
        sorted_timeframes = sorted(
            mtf_data.keys(),
            key=lambda x: timeframe_order.index(x) if x in timeframe_order else 999
        )

        for tf in sorted_timeframes:
            ohlcv, close_series = mtf_data[tf]

            if ohlcv is None or len(ohlcv) == 0:
                continue

            # Extract latest candle data
            latest = ohlcv[-1]
            timestamp, open_price, high, low, close, volume = latest

            # Calculate price change
            if len(close_series) >= 2:
                prev_close = close_series[-2]
                price_change = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0
            else:
                price_change = 0

            # Calculate volume average
            if len(ohlcv) >= 20:
                recent_volumes = ohlcv[-20:, 5]  # Last 20 candles' volume
                avg_volume = np.mean(recent_volumes)
                volume_ratio = volume / avg_volume if avg_volume > 0 else 0
            else:
                volume_ratio = 1.0

            # Format timeframe section
            lines.append(f"🕐 {tf.upper()} Timeframe:")
            lines.append(f"   Price: ${close:,.2f} ({price_change:+.2f}%)")
            lines.append(f"   Range: ${low:,.2f} - ${high:,.2f}")
            lines.append(f"   Volume: {volume:,.0f} ({volume_ratio:.2f}x avg)")
            lines.append(f"   Candles: {len(ohlcv)}")
            lines.append("")

        lines.append("=" * 90)
        return "\n".join(lines)

    @staticmethod
    def format_timeframe_alignment(mtf_data: Dict[str, Any]) -> str:
        """
        Analyze and format timeframe alignment (trend consistency across timeframes).

        Args:
            mtf_data: Dictionary with timeframe keys and (ohlcv, close_series) values

        Returns:
            Formatted alignment analysis string
        """
        if not mtf_data or len(mtf_data) < 2:
            return ""

        lines = [
            "=" * 90,
            "🔍 TIMEFRAME ALIGNMENT ANALYSIS",
            "=" * 90,
            ""
        ]

        # Analyze trend direction for each timeframe
        timeframe_trends = {}
        for tf, (ohlcv, close_series) in mtf_data.items():
            if close_series is None or len(close_series) < 10:
                continue

            # Simple trend: compare recent price to moving average
            recent_close = close_series[-1]
            ma_period = min(20, len(close_series) - 1)
            ma = np.mean(close_series[-ma_period:])

            if recent_close > ma * 1.01:
                trend = "BULLISH ↗"
            elif recent_close < ma * 0.99:
                trend = "BEARISH ↘"
            else:
                trend = "NEUTRAL ↔"

            timeframe_trends[tf] = trend

        # Display alignment
        lines.append("Trend Direction by Timeframe:")
        timeframe_order = ['5m', '15m', '1h', '4h', '12h', '1d']
        for tf in timeframe_order:
            if tf in timeframe_trends:
                lines.append(f"   {tf.upper():6} → {timeframe_trends[tf]}")

        # Check for alignment
        trends = list(timeframe_trends.values())
        if trends.count("BULLISH ↗") == len(trends):
            lines.append("\n✅ STRONG ALIGNMENT: All timeframes BULLISH")
        elif trends.count("BEARISH ↘") == len(trends):
            lines.append("\n✅ STRONG ALIGNMENT: All timeframes BEARISH")
        elif trends.count("BULLISH ↗") >= len(trends) * 0.7:
            lines.append("\n⚠️ PARTIAL ALIGNMENT: Majority BULLISH")
        elif trends.count("BEARISH ↘") >= len(trends) * 0.7:
            lines.append("\n⚠️ PARTIAL ALIGNMENT: Majority BEARISH")
        else:
            lines.append("\n❌ NO ALIGNMENT: Mixed signals across timeframes")

        lines.append("")
        lines.append("=" * 90)
        return "\n".join(lines)

    @staticmethod
    def format_timeframe_data_compact(mtf_data: Dict[str, Any]) -> str:
        """
        Format multi-timeframe data in compact format for token efficiency.

        Args:
            mtf_data: Dictionary with timeframe keys

        Returns:
            Compact formatted string
        """
        if not mtf_data:
            return ""

        lines = ["📊 MTF Summary:"]

        timeframe_order = ['5m', '15m', '1h', '4h', '12h', '1d']
        for tf in timeframe_order:
            if tf not in mtf_data:
                continue

            ohlcv, close_series = mtf_data[tf]
            if ohlcv is None or len(ohlcv) == 0:
                continue

            latest = ohlcv[-1]
            close = latest[4]
            volume = latest[5]

            # Price change
            if len(close_series) >= 2:
                prev_close = close_series[-2]
                change_pct = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0
            else:
                change_pct = 0

            lines.append(f"{tf.upper()}: ${close:,.2f} ({change_pct:+.1f}%) Vol:{volume:,.0f}")

        return " | ".join(lines)

    @staticmethod
    def format_divergence_signals(divergence_data: Dict[str, Any]) -> str:
        """
        Format divergence signals for AI consumption

        Args:
            divergence_data: Divergence analysis results from debate_agent

        Returns:
            Formatted string with clear divergence information
        """
        if not divergence_data or 'timeframe' not in divergence_data:
            return ""

        tf = divergence_data.get('timeframe', 'unknown')
        lines = [f"\n🎯 DIVERGENCE ANALYSIS (Timeframe: {tf.upper()})"]
        lines.append("=" * 90)

        # Stochastic Divergence
        stoch = divergence_data.get('stochastic', {})
        lines.append(f"\n📊 Stochastic Divergence (Current Value: {stoch.get('current_value', 50):.1f}):")
        lines.append(f"  ├─ Regular Bullish: {stoch.get('regular_bullish', False)} (Strength: {stoch.get('regular_strength', 0):.1f})")
        lines.append(f"  ├─ Regular Bearish: {stoch.get('regular_bearish', False)} (Strength: {stoch.get('regular_strength', 0):.1f})")
        lines.append(f"  ├─ Hidden Bullish: {stoch.get('hidden_bullish', False)} (Strength: {stoch.get('hidden_strength', 0):.1f}) ✅ BUY DIP")
        lines.append(f"  └─ Hidden Bearish: {stoch.get('hidden_bearish', False)} (Strength: {stoch.get('hidden_strength', 0):.1f}) ✅ SELL RALLY")

        # RSI Divergence
        rsi = divergence_data.get('rsi', {})
        lines.append(f"\n📈 RSI Divergence (Current Value: {rsi.get('current_value', 50):.1f}):")
        lines.append(f"  ├─ Regular Bullish: {rsi.get('regular_bullish', False)} (Strength: {rsi.get('regular_strength', 0):.1f})")
        lines.append(f"  ├─ Regular Bearish: {rsi.get('regular_bearish', False)} (Strength: {rsi.get('regular_strength', 0):.1f})")
        lines.append(f"  ├─ Hidden Bullish: {rsi.get('hidden_bullish', False)} (Strength: {rsi.get('hidden_strength', 0):.1f})")
        lines.append(f"  └─ Hidden Bearish: {rsi.get('hidden_bearish', False)} (Strength: {rsi.get('hidden_strength', 0):.1f})")

        # MACD Divergence
        macd = divergence_data.get('macd', {})
        lines.append(f"\n📉 MACD Histogram Divergence (Current Value: {macd.get('current_value', 0):.4f}):")
        lines.append(f"  ├─ Regular Bullish: {macd.get('regular_bullish', False)} (Strength: {macd.get('regular_strength', 0):.1f})")
        lines.append(f"  ├─ Regular Bearish: {macd.get('regular_bearish', False)} (Strength: {macd.get('regular_strength', 0):.1f})")
        lines.append(f"  ├─ Hidden Bullish: {macd.get('hidden_bullish', False)} (Strength: {macd.get('hidden_strength', 0):.1f})")
        lines.append(f"  └─ Hidden Bearish: {macd.get('hidden_bearish', False)} (Strength: {macd.get('hidden_strength', 0):.1f})")

        # Bollinger Band Context
        bb_trend = divergence_data.get('bb_trend', 'unknown')
        bb_pos = divergence_data.get('bb_position_pct', 50)
        lines.append(f"\n🎯 Bollinger Band Context:")
        lines.append(f"  ├─ Trend Position: {bb_trend.upper()} (Price relative to BB middle)")
        lines.append(f"  └─ Band Position: {bb_pos:.1f}% (0%=lower band, 100%=upper band)")

        # Stochastic Cross Signals
        golden = divergence_data.get('stoch_golden_cross', False)
        death = divergence_data.get('stoch_death_cross', False)
        oversold = divergence_data.get('stoch_near_oversold', False)
        overbought = divergence_data.get('stoch_near_overbought', False)

        lines.append(f"\n⚡ Stochastic Cross Signals:")
        lines.append(f"  ├─ Golden Cross (K > D): {golden} {'✅ BULLISH SIGNAL' if golden else ''}")
        lines.append(f"  ├─ Death Cross (K < D): {death} {'⚠️ BEARISH SIGNAL' if death else ''}")
        lines.append(f"  ├─ Near Oversold (<25): {oversold} {'✅ BUY ZONE' if oversold else ''}")
        lines.append(f"  └─ Near Overbought (>75): {overbought} {'⚠️ SELL ZONE' if overbought else ''}")

        # Strategic Recommendations
        lines.append(f"\n🔥 STRATEGIC ENTRY SIGNALS:")

        # LONG Signals
        if (bb_trend == 'above_middle' and stoch.get('hidden_bullish', False) and
            golden and oversold):
            lines.append("  ✅ HIGHEST PRIORITY LONG: BB Above + Hidden Bull Div + Golden Cross near 20 (Confidence: 75-85%)")
        elif bb_trend == 'above_middle' and stoch.get('hidden_bullish', False):
            lines.append("  ✅ HIGH PRIORITY LONG: BB Above + Hidden Bull Div (Confidence: 65-75%)")
        elif stoch.get('hidden_bullish', False):
            lines.append("  ⚠️ MEDIUM LONG: Hidden Bull Div alone (Confidence: 55-65%)")
        elif stoch.get('regular_bullish', False):
            lines.append("  ⚠️ LOW LONG: Regular Bull Div (reversal signal, needs confirmation) (Confidence: 45-55%)")

        # SHORT Signals
        if (bb_trend == 'below_middle' and stoch.get('hidden_bearish', False) and
            death and overbought):
            lines.append("  ✅ HIGHEST PRIORITY SHORT: BB Below + Hidden Bear Div + Death Cross near 80 (Confidence: 75-85%)")
        elif bb_trend == 'below_middle' and stoch.get('hidden_bearish', False):
            lines.append("  ✅ HIGH PRIORITY SHORT: BB Below + Hidden Bear Div (Confidence: 65-75%)")
        elif stoch.get('hidden_bearish', False):
            lines.append("  ⚠️ MEDIUM SHORT: Hidden Bear Div alone (Confidence: 55-65%)")
        elif stoch.get('regular_bearish', False):
            lines.append("  ⚠️ LOW SHORT: Regular Bear Div (reversal signal, needs confirmation) (Confidence: 45-55%)")

        # Cross-Validation
        confirmations = 0
        if stoch.get('hidden_bullish', False) or stoch.get('hidden_bearish', False):
            confirmations += 1
        if rsi.get('hidden_bullish', False) or rsi.get('hidden_bearish', False):
            confirmations += 1
        if macd.get('hidden_bullish', False) or macd.get('hidden_bearish', False):
            confirmations += 1

        if confirmations >= 3:
            lines.append(f"\n✅ TRIPLE CONFIRMATION: Stoch + RSI + MACD aligned → Add +15% confidence")
        elif confirmations >= 2:
            lines.append(f"\n✅ DOUBLE CONFIRMATION: 2 indicators aligned → Add +10% confidence")
        elif confirmations >= 1:
            lines.append(f"\n⚠️ SINGLE CONFIRMATION: 1 indicator only → Add +5% confidence")

        lines.append("=" * 90)
        return "\n".join(lines)
