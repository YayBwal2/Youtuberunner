import unittest
from motion.easing import (
    linear,
    ease_out_expo,
    ease_in_out_cubic,
    ease_out_cubic,
    ease_out_back,
    spring,
    interpolate,
    get_easing
)


class TestEasing(unittest.TestCase):
    def test_endpoints_zero_and_one(self):
        """All easing curves must start at 0.0 and terminate exactly at 1.0."""
        curves = [linear, ease_out_expo, ease_in_out_cubic, ease_out_cubic, ease_out_back, spring]
        for fn in curves:
            self.assertEqual(fn(0.0), 0.0, f"{fn.__name__}(0.0) did not return 0.0")
            self.assertEqual(fn(1.0), 1.0, f"{fn.__name__}(1.0) did not return 1.0")
            self.assertEqual(fn(1.5), 1.0, f"{fn.__name__}(1.5) should be clamped to 1.0")
            self.assertEqual(fn(-0.5), 0.0, f"{fn.__name__}(-0.5) should be clamped to 0.0")

    def test_ease_out_expo_monotonicity(self):
        """Ease out expo should increase monotonically towards 1.0."""
        prev = 0.0
        for step in range(1, 101):
            t = step / 100.0
            val = ease_out_expo(t)
            self.assertGreaterEqual(val, prev, f"ease_out_expo non-monotonic at t={t}")
            prev = val
        self.assertEqual(prev, 1.0)

    def test_ease_in_out_cubic_piecewise_continuity(self):
        """Piecewise cubic curve must be continuous at midpoint t=0.5."""
        left = ease_in_out_cubic(0.49999)
        mid = ease_in_out_cubic(0.5)
        right = ease_in_out_cubic(0.50001)
        self.assertAlmostEqual(mid, 0.5, places=4)
        self.assertAlmostEqual(left, mid, places=3)
        self.assertAlmostEqual(right, mid, places=3)

    def test_spring_smoothstep_endpoint_correction(self):
        """
        Spring must have smooth settling and zero sudden cut-offs.
        The final transition to 1.0 must be continuous.
        """
        val_99 = spring(0.99)
        val_100 = spring(1.0)
        self.assertEqual(val_100, 1.0)
        self.assertLess(abs(val_99 - 1.0), 0.005)

    def test_interpolation_helper(self):
        """Interpolate properly maps start to end."""
        res_start = interpolate(100.0, 500.0, 0.0, easing="ease_out_expo")
        res_end = interpolate(100.0, 500.0, 1.0, easing="ease_out_expo")
        res_mid = interpolate(100.0, 500.0, 0.5, easing="linear")
        self.assertEqual(res_start, 100.0)
        self.assertEqual(res_end, 500.0)
        self.assertEqual(res_mid, 300.0)


if __name__ == "__main__":
    unittest.main()
