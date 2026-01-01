import numpy as np
from numba import njit

@njit(cache=True)
def ewma_numba(data, span):
    alpha = 2 / (span + 1)
    out = np.empty_like(data)
    out[0] = data[0]
    for i in range(1, len(data)):
        out[i] = alpha * data[i] + (1 - alpha) * out[i - 1]
    return out

@njit(cache=True)
def ema_numba(arr, length):
    ema_arr = np.empty_like(arr)
    multiplier = 2 / (length + 1)

    first_valid = 0
    while first_valid < len(arr) and np.isnan(arr[first_valid]):
        first_valid += 1

    if first_valid == len(arr):
        return np.full_like(arr, np.nan)

    ema_arr[first_valid] = arr[first_valid]

    for i in range(first_valid + 1, len(arr)):
        if np.isnan(arr[i]):
            ema_arr[i] = ema_arr[i - 1]
        else:
            ema_arr[i] = ((arr[i] - ema_arr[i - 1]) * multiplier) + ema_arr[i - 1]

    ema_arr[:first_valid] = np.nan

    return ema_arr


@njit(cache=True)
def sma_numba(arr, length):
    n = len(arr)
    sma_values = np.full(n, np.nan, dtype=np.float64)

    # 🔥 FORCED ACTIVATION: min_periods=1 개념 적용
    # 데이터가 부족해도 있는 만큼 계산 (부분 평균)
    if n < length:
        # 데이터가 부족하면 있는 데이터 전체의 평균을 마지막에 넣음
        if n > 0:
            sma_values[n - 1] = np.mean(arr)
        return sma_values

    window_sum = np.sum(arr[:length])
    sma_values[length - 1] = window_sum / length

    for i in range(length, n):
        window_sum += arr[i] - arr[i - length]
        sma_values[i] = window_sum / length

    return sma_values