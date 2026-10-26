from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Dict

# Reference Resolution
REFERENCE_WIDTH = 1080
REFERENCE_HEIGHT = 1920

# Safe Area Percentages (Relative to Canvas Dimensions)
# Top: YouTube Shorts header, sound info, search icon
# Bottom: Channel handle, subscribe CTA, audio progress bar
# Right: Vertical action buttons (Like, Dislike, Comment, Share, Remix)
# Left: Subtle edge margin
SAFE_TOP_RATIO = 0.1250      # 12.50% (240px @ 1920h)
SAFE_BOTTOM_RATIO = 0.1979   # 19.79% (380px @ 1920h)
SAFE_LEFT_RATIO = 0.0741     #  7.41% (80px  @ 1080w)
SAFE_RIGHT_RATIO = 0.1481    # 14.81% (160px @ 1080w)


@dataclass(frozen=True)
class SafeArea:
    x: int
    y: int
    width: int
    height: int
    right: int
    bottom: int

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2


def get_safe_area(canvas_width: int = REFERENCE_WIDTH, canvas_height: int = REFERENCE_HEIGHT) -> SafeArea:
    """Calculates responsive safe area bounding box based on reference ratios."""
    x = int(canvas_width * SAFE_LEFT_RATIO)
    y = int(canvas_height * SAFE_TOP_RATIO)
    right = canvas_width - int(canvas_width * SAFE_RIGHT_RATIO)
    bottom = canvas_height - int(canvas_height * SAFE_BOTTOM_RATIO)
    width = right - x
    height = bottom - y
    return SafeArea(x=x, y=y, width=width, height=height, right=right, bottom=bottom)


# Design Color Tokens (Dark Minimalist Developer Palette)
PALETTE: Dict[str, Tuple[int, int, int]] = {
    "bg_slate": (15, 23, 42),       # #0f172a Main Canvas
    "surface": (17, 24, 39),        # #111827 Cards / Terminal body
    "surface_title": (30, 41, 59),  # #1e293b Card Headers / Tabs
    "border": (51, 65, 85),         # #334155 Subtle 1px borders
    "primary": (34, 197, 94),       # #22c55e Neon Emerald Green
    "secondary": (56, 189, 248),    # #38bdf8 Sky Blue / Code Variables
    "warning": (245, 158, 11),      # #f59e0b Amber Alert
    "danger": (239, 68, 68),        # #ef4444 Red Accent
    "text_white": (255, 255, 255),  # #ffffff High contrast
    "text_muted": (148, 163, 184),  # #94a3b8 Slate 400
    "dot_matrix": (26, 36, 54),     # Subtle background grid dots
    "progress_bg": (30, 41, 59),    # Progress bar track
    "progress_fill": (34, 197, 94)  # Progress bar fill
}

HEX_PALETTE: Dict[str, str] = {
    name: f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    for name, rgb in PALETTE.items()
}


# Typography Scale (Scaled proportionally to canvas width)
def get_type_scale(canvas_width: int = REFERENCE_WIDTH) -> Dict[str, int]:
    scale_factor = canvas_width / REFERENCE_WIDTH
    return {
        "display": int(76 * scale_factor),
        "headline": int(64 * scale_factor),
        "subhead": int(46 * scale_factor),
        "code": int(30 * scale_factor),
        "body": int(26 * scale_factor),
        "caption": int(22 * scale_factor),
        "badge": int(18 * scale_factor)
    }


# 8px Base Spacing Grid
SPACING = {
    "xs": 8,
    "sm": 16,
    "md": 24,
    "lg": 32,
    "xl": 48,
    "2xl": 64
}

# Font Resolutions
FONTS = {
    "mono": Path("/System/Library/Fonts/SFNSMono.ttf"),
    "sans_bold": Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    "sans": Path("/System/Library/Fonts/Supplemental/Helvetica.ttc")
}

# Fallback resolution
for key, p in FONTS.items():
    if not p.exists():
        fallbacks = [
            Path("/System/Library/Fonts/SFCompact.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/Library/Fonts/Arial.ttf")
        ]
        for fb in fallbacks:
            if fb.exists():
                FONTS[key] = fb
                break
