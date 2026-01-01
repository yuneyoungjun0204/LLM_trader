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
