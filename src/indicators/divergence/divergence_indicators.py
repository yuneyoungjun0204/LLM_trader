"""
Advanced Divergence Detection Engine
Supports Regular & Hidden Divergence for Stochastic, RSI, MACD
"""
import numpy as np
from numba import njit
from typing import Tuple


@njit(cache=True)
def find_pivot_points(data: np.ndarray, left_bars: int = 5, right_bars: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find pivot high and low points in data

    Args:
        data: Price or indicator array
        left_bars: Number of bars to the left for comparison
        right_bars: Number of bars to the right for comparison

    Returns:
        Tuple of (pivot_highs, pivot_lows)
        - pivot_highs: Array with pivot high values (NaN elsewhere)
        - pivot_lows: Array with pivot low values (NaN elsewhere)
    """
    n = len(data)
    pivot_highs = np.full(n, np.nan)
    pivot_lows = np.full(n, np.nan)

    for i in range(left_bars, n - right_bars):
        # Check for pivot high
        is_pivot_high = True
        for j in range(i - left_bars, i + right_bars + 1):
            if j != i and data[j] >= data[i]:
                is_pivot_high = False
                break

        if is_pivot_high:
            pivot_highs[i] = data[i]

        # Check for pivot low
        is_pivot_low = True
        for j in range(i - left_bars, i + right_bars + 1):
            if j != i and data[j] <= data[i]:
                is_pivot_low = False
                break

        if is_pivot_low:
            pivot_lows[i] = data[i]

    return pivot_highs, pivot_lows


@njit(cache=True)
def detect_regular_divergence(price: np.ndarray, indicator: np.ndarray,
                              lookback: int = 60, pivot_bars: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Detect Regular Divergence (Trend Reversal Signal)

    Regular Bullish Divergence:
    - Price makes lower low
    - Indicator makes higher low
    - Signal: Potential upward reversal

    Regular Bearish Divergence:
    - Price makes higher high
    - Indicator makes lower high
    - Signal: Potential downward reversal

    Args:
        price: Price array (close prices)
        indicator: Indicator array (Stochastic %K, RSI, MACD Histogram)
        lookback: Maximum bars to look back for divergence
        pivot_bars: Bars for pivot point detection

    Returns:
        Tuple of (bullish_div, bearish_div, divergence_strength)
        - bullish_div: 1 where bullish divergence detected
        - bearish_div: 1 where bearish divergence detected
        - divergence_strength: 0-100 score based on divergence magnitude
    """
    n = len(price)
    bullish_div = np.zeros(n)
    bearish_div = np.zeros(n)
    divergence_strength = np.zeros(n)

    # Find pivot points
    price_highs, price_lows = find_pivot_points(price, pivot_bars, pivot_bars)
    ind_highs, ind_lows = find_pivot_points(indicator, pivot_bars, pivot_bars)

    for i in range(lookback, n):
        # Collect recent pivot lows for bullish divergence
        price_low_indices = []
        ind_low_indices = []

        for j in range(max(0, i - lookback), i):
            if not np.isnan(price_lows[j]):
                price_low_indices.append(j)
            if not np.isnan(ind_lows[j]):
                ind_low_indices.append(j)

        # Check for Regular Bullish Divergence (price lower low, indicator higher low)
        if len(price_low_indices) >= 2 and len(ind_low_indices) >= 2:
            latest_price_low_idx = price_low_indices[-1]
            prev_price_low_idx = price_low_indices[-2]

            latest_ind_low_idx = ind_low_indices[-1]
            prev_ind_low_idx = ind_low_indices[-2]

            # Price makes lower low
            if price[latest_price_low_idx] < price[prev_price_low_idx]:
                # Indicator makes higher low
                if indicator[latest_ind_low_idx] > indicator[prev_ind_low_idx]:
                    bullish_div[i] = 1

                    # Calculate divergence strength
                    price_change = (price[prev_price_low_idx] - price[latest_price_low_idx]) / price[prev_price_low_idx] * 100
                    ind_change = (indicator[latest_ind_low_idx] - indicator[prev_ind_low_idx]) / (indicator[prev_ind_low_idx] + 1e-10) * 100
                    strength = min(100, abs(price_change) + abs(ind_change))
                    divergence_strength[i] = strength

        # Collect recent pivot highs for bearish divergence
        price_high_indices = []
        ind_high_indices = []

        for j in range(max(0, i - lookback), i):
            if not np.isnan(price_highs[j]):
                price_high_indices.append(j)
            if not np.isnan(ind_highs[j]):
                ind_high_indices.append(j)

        # Check for Regular Bearish Divergence (price higher high, indicator lower high)
        if len(price_high_indices) >= 2 and len(ind_high_indices) >= 2:
            latest_price_high_idx = price_high_indices[-1]
            prev_price_high_idx = price_high_indices[-2]

            latest_ind_high_idx = ind_high_indices[-1]
            prev_ind_high_idx = ind_high_indices[-2]

            # Price makes higher high
            if price[latest_price_high_idx] > price[prev_price_high_idx]:
                # Indicator makes lower high
                if indicator[latest_ind_high_idx] < indicator[prev_ind_high_idx]:
                    bearish_div[i] = 1

                    # Calculate divergence strength
                    price_change = (price[latest_price_high_idx] - price[prev_price_high_idx]) / price[prev_price_high_idx] * 100
                    ind_change = (indicator[prev_ind_high_idx] - indicator[latest_ind_high_idx]) / (indicator[prev_ind_high_idx] + 1e-10) * 100
                    strength = min(100, abs(price_change) + abs(ind_change))
                    divergence_strength[i] = strength

    return bullish_div, bearish_div, divergence_strength


@njit(cache=True)
def detect_hidden_divergence(price: np.ndarray, indicator: np.ndarray,
                             lookback: int = 60, pivot_bars: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Detect Hidden Divergence (Trend Continuation Signal)

    Hidden Bullish Divergence (Uptrend Pullback):
    - Price makes higher low (uptrend intact)
    - Indicator makes lower low
    - Signal: Buy the dip, trend continues up

    Hidden Bearish Divergence (Downtrend Bounce):
    - Price makes lower high (downtrend intact)
    - Indicator makes higher high
    - Signal: Sell the rally, trend continues down

    Args:
        price: Price array (close prices)
        indicator: Indicator array (Stochastic %K, RSI, MACD Histogram)
        lookback: Maximum bars to look back for divergence
        pivot_bars: Bars for pivot point detection

    Returns:
        Tuple of (hidden_bullish_div, hidden_bearish_div, divergence_strength)
    """
    n = len(price)
    hidden_bullish_div = np.zeros(n)
    hidden_bearish_div = np.zeros(n)
    divergence_strength = np.zeros(n)

    # Find pivot points
    price_highs, price_lows = find_pivot_points(price, pivot_bars, pivot_bars)
    ind_highs, ind_lows = find_pivot_points(indicator, pivot_bars, pivot_bars)

    for i in range(lookback, n):
        # Collect recent pivot lows for hidden bullish divergence
        price_low_indices = []
        ind_low_indices = []

        for j in range(max(0, i - lookback), i):
            if not np.isnan(price_lows[j]):
                price_low_indices.append(j)
            if not np.isnan(ind_lows[j]):
                ind_low_indices.append(j)

        # Check for Hidden Bullish Divergence (price higher low, indicator lower low)
        if len(price_low_indices) >= 2 and len(ind_low_indices) >= 2:
            latest_price_low_idx = price_low_indices[-1]
            prev_price_low_idx = price_low_indices[-2]

            latest_ind_low_idx = ind_low_indices[-1]
            prev_ind_low_idx = ind_low_indices[-2]

            # Price makes higher low (uptrend)
            if price[latest_price_low_idx] > price[prev_price_low_idx]:
                # Indicator makes lower low
                if indicator[latest_ind_low_idx] < indicator[prev_ind_low_idx]:
                    hidden_bullish_div[i] = 1

                    # Calculate divergence strength
                    price_change = (price[latest_price_low_idx] - price[prev_price_low_idx]) / price[prev_price_low_idx] * 100
                    ind_change = (indicator[prev_ind_low_idx] - indicator[latest_ind_low_idx]) / (indicator[prev_ind_low_idx] + 1e-10) * 100
                    strength = min(100, abs(price_change) + abs(ind_change))
                    divergence_strength[i] = strength

        # Collect recent pivot highs for hidden bearish divergence
        price_high_indices = []
        ind_high_indices = []

        for j in range(max(0, i - lookback), i):
            if not np.isnan(price_highs[j]):
                price_high_indices.append(j)
            if not np.isnan(ind_highs[j]):
                ind_high_indices.append(j)

        # Check for Hidden Bearish Divergence (price lower high, indicator higher high)
        if len(price_high_indices) >= 2 and len(ind_high_indices) >= 2:
            latest_price_high_idx = price_high_indices[-1]
            prev_price_high_idx = price_high_indices[-2]

            latest_ind_high_idx = ind_high_indices[-1]
            prev_ind_high_idx = ind_high_indices[-2]

            # Price makes lower high (downtrend)
            if price[latest_price_high_idx] < price[prev_price_high_idx]:
                # Indicator makes higher high
                if indicator[latest_ind_high_idx] > indicator[prev_ind_high_idx]:
                    hidden_bearish_div[i] = 1

                    # Calculate divergence strength
                    price_change = (price[prev_price_high_idx] - price[latest_price_high_idx]) / price[prev_price_high_idx] * 100
                    ind_change = (indicator[latest_ind_high_idx] - indicator[prev_ind_high_idx]) / (indicator[prev_ind_high_idx] + 1e-10) * 100
                    strength = min(100, abs(price_change) + abs(ind_change))
                    divergence_strength[i] = strength

    return hidden_bullish_div, hidden_bearish_div, divergence_strength
