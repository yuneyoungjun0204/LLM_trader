import numpy as np
from numba import njit


@njit(cache=True)
def atr_numba(high, low, close, length=14, mamode='rma', percent=False):
    n = len(high)
    atr = np.empty(n)
    tr = np.empty(n)

    atr[:length] = np.nan
    tr[0] = 0

    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))

    if np.any(np.isnan(tr)) or np.any(np.isnan(high)) or np.any(np.isnan(low)) or np.any(np.isnan(close)):
        return np.full(n, np.inf)

    if mamode == 'ema':
        atr[length - 1] = np.mean(tr[1:length])
        alpha = 2 / (length + 1)
        for i in range(length, n):
            atr[i] = (1 - alpha) * atr[i - 1] + alpha * tr[i]
    elif mamode == 'sma':
        sum_tr = np.sum(tr[1:length])
        for i in range(length, n):
            atr[i] = sum_tr / length
            sum_tr += tr[i] - tr[i - length + 1]
    elif mamode == 'wma':
        weights = np.arange(1, length + 1).astype(np.float64)
        weight_sum = np.sum(weights)
        for i in range(length, n):
            atr[i] = np.dot(tr[i - length + 1:i + 1], weights) / weight_sum
    else:
        atr[length - 1] = np.mean(tr[1:length])
        for i in range(length, n):
            atr[i] = (atr[i - 1] * (length - 1) + tr[i]) / length

    if percent:
        atr[length:] *= 100 / close[length:]

    return atr

@njit(cache=True)
def bollinger_bands_numba(close, length, num_std_dev):
    n = len(close)
    upper_band = np.full(n, np.nan)
    lower_band = np.full(n, np.nan)
    middle_band = np.full(n, np.nan)

    for i in range(length - 1, n):
        window = close[i - length + 1:i + 1]
        mean = np.mean(window)
        std = np.sqrt(np.sum((window - mean) ** 2) / (len(window) - 0))
        upper_band[i] = mean + (std * num_std_dev)
        middle_band[i] = mean
        lower_band[i] = mean - (std * num_std_dev)

    return upper_band, middle_band, lower_band

@njit(cache=True)
def chandelier_exit_numba(high, low, close, length, multiplier, mamode='rma'):
    n = len(close)
    atr_values = atr_numba(high, low, close, length, mamode)

    chandelier_exit_long = np.empty(n, dtype=np.float64)
    chandelier_exit_short = np.empty(n, dtype=np.float64)

    chandelier_exit_long[0:length] = 0
    chandelier_exit_short[0:length] = 0

    for i in range(length - 1, n):
        period_high = np.max(high[i - length + 1:i + 1])
        period_low = np.min(low[i - length + 1:i + 1])

        # Calculate the chandelier exits
        chandelier_exit_long[i] = period_high - atr_values[i] * multiplier
        chandelier_exit_short[i] = period_low + atr_values[i] * multiplier

    return chandelier_exit_long, chandelier_exit_short


@njit(cache=True)
def ebsw_numba(close, length=40, bars=10):
    n = len(close)
    ebsw = np.full(n, np.nan)

    last_close = last_hp = 0
    filter_hist = np.zeros(2)

    for i in range(length, n):
        alpha1 = (1 - np.sin(np.pi * 360 / length)) / np.cos(np.pi * 360 / length)
        hp = 0.5 * (1 + alpha1) * (close[i] - last_close) + alpha1 * last_hp

        a1 = np.exp(-np.sqrt(2) * np.pi / bars)
        b1 = 2 * a1 * np.cos(np.sqrt(2) * np.pi * 180 / bars)
        c2 = b1
        c3 = -1 * a1 * a1
        c1 = 1 - c2 - c3
        filt = c1 * (hp + last_hp) / 2 + c2 * filter_hist[1] + c3 * filter_hist[0]

        wave = (filt + filter_hist[1] + filter_hist[0]) / 3
        pwr = (filt * filt + filter_hist[1] * filter_hist[1] + filter_hist[0] * filter_hist[0]) / 3

        wave = wave / np.sqrt(pwr)

        filter_hist[0] = filter_hist[1]
        filter_hist[1] = filt
        last_hp = hp
        last_close = close[i]
        ebsw[i] = wave

    return ebsw


@njit(cache=True)
def vhf_numba(close, length=28, drift=1):
    n = len(close)
    if n < length:
        return np.full(n, np.nan)

    vhf = np.full(n, np.nan)

    for i in range(length - 1 + drift, n):
        hcp = np.max(close[i - length + 1:i + 1:drift])
        lcp = np.min(close[i - length + 1:i + 1:drift])

        sliced_close = close[i - length + 1:i + 1:drift]

        # Manually compute the differences
        diff = np.abs(sliced_close[1:] - sliced_close[:-1])
        sum_diff = np.sum(diff)

        # Handle division by zero
        if sum_diff != 0:
            vhf[i] = np.abs(hcp - lcp) / sum_diff
        else:
            vhf[i] = 0

    return vhf


@njit(cache=True)
def donchian_channels_numba(high, low, length=20):
    """Calculate Donchian Channels
    
    Args:
        high: High prices array
        low: Low prices array  
        length: Period for calculation (default: 20)
        
    Returns:
        Tuple of (upper_channel, middle_channel, lower_channel)
    """
    n = len(high)
    
    upper_channel = np.full(n, np.nan)
    lower_channel = np.full(n, np.nan)
    middle_channel = np.full(n, np.nan)
    
    # Calculate rolling max and min
    for i in range(length - 1, n):
        upper_channel[i] = np.max(high[i - length + 1:i + 1])
        lower_channel[i] = np.min(low[i - length + 1:i + 1])
        middle_channel[i] = (upper_channel[i] + lower_channel[i]) / 2.0
        
    return upper_channel, middle_channel, lower_channel


@njit(cache=True)
def keltner_channels_numba(high, low, close, length=20, multiplier=2.0, mamode='ema'):
    """Calculate Keltner Channels"""
    n = len(close)
    
    # Calculate middle line (EMA of close prices)
    middle = np.full(n, np.nan)
    upper = np.full(n, np.nan)
    lower = np.full(n, np.nan)
    
    # Calculate ATR
    tr = np.full(n, np.nan)
    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
    
    # Calculate EMA for middle line
    alpha = 2.0 / (length + 1)
    middle[length - 1] = np.mean(close[:length])
    for i in range(length, n):
        middle[i] = alpha * close[i] + (1 - alpha) * middle[i - 1]
    
    # Calculate ATR EMA
    atr_ema = np.full(n, np.nan)
    atr_ema[length - 1] = np.mean(tr[1:length])
    for i in range(length, n):
        atr_ema[i] = alpha * tr[i] + (1 - alpha) * atr_ema[i - 1]
    
    # Calculate upper and lower bands
    for i in range(length - 1, n):
        if not np.isnan(middle[i]) and not np.isnan(atr_ema[i]):
            upper[i] = middle[i] + multiplier * atr_ema[i]
            lower[i] = middle[i] - multiplier * atr_ema[i]
    
    return upper, middle, lower


@njit(cache=True)
def choppiness_index_numba(high, low, close, length=14):
    """Calculate Choppiness Index (CI)

    The Choppiness Index measures market choppiness vs trending behavior.
    - Values > 61.8: Market is choppy/ranging (low directional movement)
    - Values < 38.2: Market is trending (strong directional movement)
    - Values between: Transitional state

    Args:
        high: High prices array
        low: Low prices array
        close: Close prices array
        length: Period for calculation (default: 14)

    Returns:
        Choppiness Index array (0-100 scale)
    """
    n = len(high)
    ci = np.full(n, np.nan)

    for i in range(length, n):
        # Calculate True Range for the period
        true_range_sum = 0.0
        for j in range(i - length + 1, i + 1):
            if j > 0:
                tr = max(
                    high[j] - low[j],
                    abs(high[j] - close[j - 1]),
                    abs(low[j] - close[j - 1])
                )
                true_range_sum += tr

        # Calculate highest high and lowest low over the period
        period_high = np.max(high[i - length + 1:i + 1])
        period_low = np.min(low[i - length + 1:i + 1])

        # Calculate Choppiness Index
        # CI = 100 * log10(sum(TR) / (highest_high - lowest_low)) / log10(length)
        range_hl = period_high - period_low

        if range_hl > 0 and true_range_sum > 0:
            ci[i] = 100.0 * np.log10(true_range_sum / range_hl) / np.log10(length)
        else:
            ci[i] = 50.0  # Neutral value when range is zero

    return ci


@njit(cache=True)
def bb_squeeze_detection_numba(upper_band, middle_band, lower_band, lookback=20):
    """Detect Bollinger Bands Squeeze (low volatility periods)

    Squeeze occurs when bands are extremely narrow relative to recent history.
    This indicates low volatility and potential for explosive breakout.

    Args:
        upper_band: Bollinger upper band array
        middle_band: Bollinger middle band array
        lower_band: Bollinger lower band array
        lookback: Period to compare current width against (default: 20)

    Returns:
        Tuple of (squeeze_detected, bandwidth_percentile, is_extreme_squeeze)
        - squeeze_detected: 1 if in squeeze, 0 otherwise
        - bandwidth_percentile: Current bandwidth vs historical (0-100)
        - is_extreme_squeeze: 1 if bandwidth in bottom 10% (extreme squeeze)
    """
    n = len(upper_band)
    squeeze_detected = np.zeros(n)
    bandwidth_percentile = np.full(n, np.nan)
    is_extreme_squeeze = np.zeros(n)

    for i in range(lookback, n):
        if np.isnan(upper_band[i]) or np.isnan(lower_band[i]) or np.isnan(middle_band[i]):
            continue

        # Calculate bandwidth (band width / middle band)
        current_bandwidth = (upper_band[i] - lower_band[i]) / middle_band[i] * 100

        # Get historical bandwidths for comparison
        historical_bandwidths = []
        for j in range(i - lookback, i):
            if not np.isnan(upper_band[j]) and not np.isnan(lower_band[j]) and middle_band[j] > 0:
                bw = (upper_band[j] - lower_band[j]) / middle_band[j] * 100
                historical_bandwidths.append(bw)

        if len(historical_bandwidths) > 0:
            historical_bandwidths_arr = np.array(historical_bandwidths)

            # Calculate percentile rank (lower = tighter squeeze)
            count_below = np.sum(historical_bandwidths_arr < current_bandwidth)
            percentile = (count_below / len(historical_bandwidths)) * 100
            bandwidth_percentile[i] = percentile

            # Squeeze detected if in bottom 30% of recent bandwidth
            if percentile < 30:
                squeeze_detected[i] = 1

            # Extreme squeeze if in bottom 10%
            if percentile < 10:
                is_extreme_squeeze[i] = 1

    return squeeze_detected, bandwidth_percentile, is_extreme_squeeze


@njit(cache=True)
def bb_breakout_detection_numba(close, upper_band, lower_band, volume, volume_ma,
                                 squeeze_detected, lookback=5):
    """Detect Bollinger Bands Breakout with volume confirmation

    Valid breakout requires:
    1. Price breaks above/below bands
    2. Volume exceeds average (confirms strength)
    3. Previous squeeze period (energy buildup)

    Args:
        close: Close prices array
        upper_band: Bollinger upper band array
        lower_band: Bollinger lower band array
        volume: Volume array
        volume_ma: Volume moving average array
        squeeze_detected: Squeeze detection array from bb_squeeze_detection_numba
        lookback: Periods to look back for previous squeeze (default: 5)

    Returns:
        Tuple of (breakout_signal, breakout_strength)
        - breakout_signal: 1 (bullish breakout), -1 (bearish breakout), 0 (no breakout)
        - breakout_strength: 0-100 score based on volume surge and band penetration
    """
    n = len(close)
    breakout_signal = np.zeros(n)
    breakout_strength = np.zeros(n)

    for i in range(lookback + 1, n):
        if np.isnan(close[i]) or np.isnan(upper_band[i]) or np.isnan(lower_band[i]):
            continue

        if np.isnan(volume[i]) or np.isnan(volume_ma[i]) or volume_ma[i] == 0:
            continue

        # Check for previous squeeze within lookback period
        had_recent_squeeze = False
        for j in range(max(0, i - lookback), i):
            if squeeze_detected[j] == 1:
                had_recent_squeeze = True
                break

        if not had_recent_squeeze:
            continue

        # Calculate volume surge (current volume vs MA)
        volume_surge = (volume[i] / volume_ma[i] - 1) * 100

        # Volume must be above average for valid breakout
        if volume_surge < 0:
            continue

        # Check for bullish breakout (close above upper band)
        if close[i] > upper_band[i]:
            band_penetration = (close[i] - upper_band[i]) / upper_band[i] * 100
            strength = min(100, (volume_surge * 0.6 + band_penetration * 100 * 0.4))

            breakout_signal[i] = 1
            breakout_strength[i] = strength

        # Check for bearish breakout (close below lower band)
        elif close[i] < lower_band[i]:
            band_penetration = (lower_band[i] - close[i]) / lower_band[i] * 100
            strength = min(100, (volume_surge * 0.6 + band_penetration * 100 * 0.4))

            breakout_signal[i] = -1
            breakout_strength[i] = strength

    return breakout_signal, breakout_strength
