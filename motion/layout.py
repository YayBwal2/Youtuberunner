from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from PIL import ImageFont

from motion.tokens import (
    REFERENCE_WIDTH,
    REFERENCE_HEIGHT,
    SafeArea,
    get_safe_area,
    SPACING,
    FONTS
)
from motion.schema import SemanticSlot


@dataclass(frozen=True)
class LayoutBox:
    x: int
    y: int
    width: int
    height: int
    slot: SemanticSlot

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


class LayoutEngine:
    """
    Deterministic Layout Engine managing safe areas, slot coordinates, and typography line fitting.
    """
    def __init__(self, canvas_width: int = REFERENCE_WIDTH, canvas_height: int = REFERENCE_HEIGHT):
        self.width = canvas_width
        self.height = canvas_height
        self.safe_area = get_safe_area(canvas_width, canvas_height)
        self._slots = self._compute_slots()

    def _compute_slots(self) -> Dict[SemanticSlot, LayoutBox]:
        sa = self.safe_area
        
        # 1. Headline Top (Safe top area: 240px to 400px)
        headline_h = 160
        headline_box = LayoutBox(
            x=sa.x,
            y=sa.y,
            width=sa.width,
            height=headline_h,
            slot=SemanticSlot.HEADLINE_TOP
        )

        # 2. Hero Card (Main stage: 440px to 1200px)
        hero_y = sa.y + headline_h + 30
        hero_h = 740
        hero_box = LayoutBox(
            x=sa.x,
            y=hero_y,
            width=sa.width,
            height=hero_h,
            slot=SemanticSlot.HERO_CARD
        )

        # 3. Card Center (Middle 50% of safe canvas)
        center_h = 680
        center_y = sa.center_y - center_h // 2
        center_box = LayoutBox(
            x=sa.x,
            y=center_y,
            width=sa.width,
            height=center_h,
            slot=SemanticSlot.CARD_CENTER
        )

        # 4. Diagram Split (Mid stage: same bounds as Hero Card)
        diag_box = LayoutBox(
            x=sa.x,
            y=hero_y,
            width=sa.width,
            height=hero_h,
            slot=SemanticSlot.DIAGRAM_SPLIT
        )

        # 5. Ticker Bottom (Lower third: 1260px to 1540px)
        ticker_y = hero_y + hero_h + 30
        ticker_h = sa.bottom - ticker_y
        ticker_box = LayoutBox(
            x=sa.x,
            y=ticker_y,
            width=sa.width,
            height=ticker_h,
            slot=SemanticSlot.TICKER_BOTTOM
        )

        return {
            SemanticSlot.HEADLINE_TOP: headline_box,
            SemanticSlot.HERO_CARD: hero_box,
            SemanticSlot.CARD_CENTER: center_box,
            SemanticSlot.DIAGRAM_SPLIT: diag_box,
            SemanticSlot.TICKER_BOTTOM: ticker_box
        }

    def get_slot_box(self, slot: SemanticSlot) -> LayoutBox:
        """Returns the precomputed bounding box for a semantic layout slot."""
        return self._slots.get(slot, self._slots[SemanticSlot.CARD_CENTER])

    @staticmethod
    def wrap_text_to_width(
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int
    ) -> List[str]:
        """
        Calculates optimal line breaks to prevent text clipping.
        Preserves complete words and returns wrapped lines.
        """
        words = text.strip().split()
        if not words:
            return []

        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Single word exceeds width, force append
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        return lines
