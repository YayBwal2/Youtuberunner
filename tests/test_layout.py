import unittest
from PIL import ImageFont
from motion.tokens import REFERENCE_WIDTH, REFERENCE_HEIGHT, get_safe_area, FONTS
from motion.layout import LayoutEngine, LayoutBox
from motion.schema import SemanticSlot


class TestLayout(unittest.TestCase):
    def test_safe_area_bounds(self):
        """Verify safe area calculations stay strictly within 1080x1920 reference dimensions."""
        sa = get_safe_area(REFERENCE_WIDTH, REFERENCE_HEIGHT)
        self.assertGreater(sa.x, 0)
        self.assertGreater(sa.y, 0)
        self.assertLess(sa.right, REFERENCE_WIDTH)
        self.assertLess(sa.bottom, REFERENCE_HEIGHT)
        self.assertGreater(sa.width, 800)
        self.assertGreater(sa.height, 1200)

    def test_semantic_slots_exist_and_bounded(self):
        """Verify all 5 slots are properly positioned within the safe canvas."""
        engine = LayoutEngine(REFERENCE_WIDTH, REFERENCE_HEIGHT)
        sa = engine.safe_area

        slots = [
            SemanticSlot.HEADLINE_TOP,
            SemanticSlot.HERO_CARD,
            SemanticSlot.CARD_CENTER,
            SemanticSlot.DIAGRAM_SPLIT,
            SemanticSlot.TICKER_BOTTOM
        ]

        for slot in slots:
            box = engine.get_slot_box(slot)
            self.assertIsInstance(box, LayoutBox)
            self.assertGreaterEqual(box.x, sa.x)
            self.assertLessEqual(box.right, sa.right)
            self.assertGreaterEqual(box.y, sa.y)
            self.assertLessEqual(box.bottom, sa.bottom)
            self.assertGreater(box.width, 0)
            self.assertGreater(box.height, 0)

    def test_wrap_text_to_width(self):
        """Ensure long strings are wrapped without words being clipped."""
        font = ImageFont.truetype(str(FONTS["mono"]), 32)
        max_w = 400
        long_text = "The quick brown fox jumps over the lazy dog and writes clean Python code"
        lines = LayoutEngine.wrap_text_to_width(long_text, font, max_w)

        self.assertGreater(len(lines), 1)
        for line in lines:
            bbox = font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            self.assertLessEqual(line_w, max_w, f"Line '{line}' exceeds max width {max_w} (got {line_w})")


if __name__ == "__main__":
    unittest.main()
