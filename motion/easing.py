import math
from typing import Callable, Union

EasingFunction = Callable[[float], float]


def linear(t: float) -> float:
    """Linear progression clamped between 0 and 1."""
    return max(0.0, min(1.0, t))


def ease_out_expo(t: float) -> float:
    """
    Exponential deceleration curve.
    Starts extremely fast and lands with silky smoothness.
    Strictly clamped at endpoints to guarantee exact 1.0 termination.
    """
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return 1.0 - math.pow(2.0, -10.0 * t)


def ease_in_out_cubic(t: float) -> float:
    """
    Full piecewise cubic S-curve.
    Smooth start, accelerating mid-flight, smooth deceleration to stop.
    """
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    if t < 0.5:
        return 4.0 * t * t * t
    else:
        return 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0


def ease_out_cubic(t: float) -> float:
    """Smooth cubic deceleration."""
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return 1.0 - math.pow(1.0 - t, 3)


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Subtle overshoot pop-in for UI cards."""
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    t -= 1.0
    return t * t * ((overshoot + 1.0) * t + overshoot) + 1.0


def spring(
    t: float,
    stiffness: float = 180.0,
    damping: float = 14.0,
    mass: float = 1.0,
    settle_threshold: float = 0.001
) -> float:
    """
    Damped harmonic spring oscillator with guaranteed endpoint stabilization.
    Prevents abrupt cutoff at settle_time by applying smoothstep tail blending
    to guarantee exact 1.0 position and 0.0 velocity at t >= 1.0.
    """
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0

    # Physical parameters
    omega_0 = math.sqrt(stiffness / mass)
    zeta = damping / (2.0 * math.sqrt(mass * stiffness))

    if zeta >= 1.0:
        # Overdamped fallback
        return ease_out_cubic(t)

    omega_d = omega_0 * math.sqrt(1.0 - zeta * zeta)
    decay = math.exp(-zeta * omega_0 * t)

    osc = math.cos(omega_d * t) + (zeta / math.sqrt(1.0 - zeta * zeta)) * math.sin(omega_d * t)
    raw_val = 1.0 - decay * osc

    # Endpoint correction: in the final 25% of progress (0.75 to 1.0),
    # smoothly decay the residual oscillation envelope to zero using Hermite smoothstep.
    # This prevents any sudden snap or residual jitter at t=1.0.
    if t > 0.75:
        p = (t - 0.75) / 0.25
        blend = 1.0 - (p * p * (3.0 - 2.0 * p))  # 1.0 down to 0.0
        return 1.0 + (raw_val - 1.0) * blend

    return raw_val


EASING_MAP: dict[str, EasingFunction] = {
    "linear": linear,
    "ease_out_expo": ease_out_expo,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_out_back": ease_out_back,
    "spring": spring
}


def get_easing(name: str) -> EasingFunction:
    """Retrieve easing function by name with safe fallback to ease_out_expo."""
    return EASING_MAP.get(name.lower(), ease_out_expo)


def interpolate(
    start_val: float,
    end_val: float,
    progress: float,
    easing: Union[str, EasingFunction] = "ease_out_expo"
) -> float:
    """Interpolate between two float values applying selected easing."""
    fn = get_easing(easing) if isinstance(easing, str) else easing
    eased_p = fn(progress)
    return start_val + (end_val - start_val) * eased_p
