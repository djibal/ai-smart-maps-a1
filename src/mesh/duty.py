import numpy as np


def expected_scan_latency_ms(duty_cycle, cycle_ms=100.0):
    sleep_ms = cycle_ms * (1.0 - duty_cycle)
    p_sleep = 1.0 - duty_cycle
    return (sleep_ms / 2.0) * p_sleep


def sample_receive_delay_ms(duty_cycle, cycle_ms, rng, n):
    sleep_ms = cycle_ms * (1.0 - duty_cycle)
    p_sleep = 1.0 - duty_cycle
    if sleep_ms <= 0:
        return np.zeros(n)
    is_sleep = rng.random(n) < p_sleep
    delays = rng.uniform(0, sleep_ms, n) * is_sleep
    return delays


def battery_pct_per_day(duty_cycle, battery_mah=3000.0,
                        scan_ma=10.0, sleep_ma=0.01):
    avg_ma = duty_cycle * scan_ma + (1 - duty_cycle) * sleep_ma
    daily_mah = avg_ma * 24.0
    return daily_mah / battery_mah * 100.0
