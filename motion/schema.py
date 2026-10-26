from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class SemanticSlot(str, Enum):
    HERO_CARD = "hero_card"
    HEADLINE_TOP = "headline_top"
    CARD_CENTER = "card_center"
    DIAGRAM_SPLIT = "diagram_split"
    TICKER_BOTTOM = "ticker_bottom"


class ComponentType(str, Enum):
    CODE_TERMINAL = "CodeTerminal"
    KINETIC_HEADLINE = "KineticHeadline"
    ARCHITECTURE_DIAGRAM = "ArchitectureDiagram"
    METRIC_CARD = "MetricCard"
    STATUS_PILL = "StatusPill"
    HOOK_TYPO_HERO = "HookTypoHero"
    PROGRESSIVE_STAGE = "ProgressiveStage"
    PAYOFF_VERDICT_CARD = "PayoffVerdictCard"


class MotionSpec(BaseModel):
    enter: str = Field(default="spring_pop_in", description="Entrance animation preset")
    exit: str = Field(default="none", description="Exit animation preset")
    delay: float = Field(default=0.0, ge=0.0, description="Delay in seconds relative to scene start")
    duration: float = Field(default=0.6, gt=0.0, description="Animation duration in seconds")
    easing: str = Field(default="ease_out_expo", description="Easing curve name")
    properties: List[str] = Field(default_factory=lambda: ["opacity", "translate_y", "scale"], description="Animated property keys")
    layer_order: int = Field(default=1, description="Z-index order (higher renders on top)")


# Pre-configured motion presets so LLM only needs to specify the visual intent
MOTION_PRESETS: Dict[str, Dict[str, Any]] = {
    "spring_pop_in": {
        "enter": "spring_pop_in",
        "exit": "none",
        "delay": 0.0,
        "duration": 0.65,
        "easing": "spring",
        "properties": ["opacity", "translate_y", "scale"],
        "layer_order": 1
    },
    "mask_reveal_up": {
        "enter": "mask_reveal_up",
        "exit": "none",
        "delay": 0.1,
        "duration": 0.50,
        "easing": "ease_out_expo",
        "properties": ["opacity", "translate_y"],
        "layer_order": 2
    },
    "fade_slide_up": {
        "enter": "fade_slide_up",
        "exit": "fade_slide_down",
        "delay": 0.15,
        "duration": 0.55,
        "easing": "ease_out_cubic",
        "properties": ["opacity", "translate_y"],
        "layer_order": 1
    },
    "diagram_grow": {
        "enter": "diagram_grow",
        "exit": "none",
        "delay": 0.20,
        "duration": 0.70,
        "easing": "ease_out_expo",
        "properties": ["opacity", "scale"],
        "layer_order": 2
    }
}


class ComponentSpec(BaseModel):
    type: ComponentType = Field(description="Reusable motion component type")
    slot: SemanticSlot = Field(default=SemanticSlot.CARD_CENTER, description="Semantic layout anchor")
    props: Dict[str, Any] = Field(default_factory=dict, description="Component-specific properties")
    motion: MotionSpec = Field(default_factory=MotionSpec, description="Animation timing and easing")


class SceneSpec(BaseModel):
    scene_id: str = Field(description="Unique scene identifier")
    narration_ref: str = Field(default="", description="Reference to voice sentence/beat")
    slot: SemanticSlot = Field(default=SemanticSlot.HERO_CARD, description="Main scene composition anchor")
    visual_intent: str = Field(default="", description="Director intent description")
    components: List[ComponentSpec] = Field(default_factory=list, description="Components within this scene")
    transition_out: Dict[str, Any] = Field(default_factory=lambda: {"type": "none", "duration": 0.2})
    estimated_duration: Optional[float] = Field(default=None, description="Optional target duration")


class Storyboard(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Storyboard schema version")
    fps: int = Field(default=30, ge=24, le=60, description="Target framerate")
    canvas_profile: str = Field(default="9:16_1080x1920", description="Target aspect ratio profile")
    title: str = Field(default="Untitled", description="Video title")
    scenes: List[SceneSpec] = Field(min_length=1, description="List of sequential scenes")

    @field_validator("schema_version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v.startswith("1."):
            raise ValueError(f"Unsupported schema version: '{v}'. Expected 1.x.x")
        return v

    @field_validator("canvas_profile")
    @classmethod
    def validate_canvas_profile(cls, v: str) -> str:
        allowed = ["9:16_1080x1920", "16:9_1920x1080"]
        if v not in allowed:
            raise ValueError(f"Unsupported canvas_profile: '{v}'. Supported profiles: {allowed}")
        return v


class StoryboardValidationError(Exception):
    """Explicit validation exception when Storyboard structure or component is invalid."""
    pass


def validate_storyboard(raw_dict: Dict[str, Any], strict: bool = True) -> Storyboard:
    """
    Validates storyboard dictionary against Pydantic schema.
    If strict=True: Raises StoryboardValidationError with clear descriptive failure details.
    If strict=False: Logs warnings and attempts automated recovery with fallback presets.
    """
    try:
        return Storyboard.model_validate(raw_dict)
    except Exception as e:
        err_msg = f"Storyboard Schema Validation Failed: {e}"
        if strict:
            # Check for known component type mismatch
            scenes = raw_dict.get("scenes", [])
            valid_types = [t.value for t in ComponentType]
            for s in scenes:
                for c in s.get("components", []):
                    c_type = c.get("type")
                    if c_type not in valid_types:
                        err_msg = (
                            f"Unknown ComponentType '{c_type}'. "
                            f"Allowed component types are: {valid_types}."
                        )
                        break
            raise StoryboardValidationError(err_msg) from e
        else:
            print(f"[WARN] {err_msg}. Applying automated fallback recovery...")
            return Storyboard(
                schema_version="1.0.0",
                fps=raw_dict.get("fps", 30),
                canvas_profile=raw_dict.get("canvas_profile", "9:16_1080x1920"),
                title=raw_dict.get("title", "Recovered Project"),
                scenes=[
                    SceneSpec(
                        scene_id="fallback_scene_01",
                        narration_ref="all",
                        slot=SemanticSlot.HERO_CARD,
                        visual_intent="Automated fallback scene",
                        components=[
                            ComponentSpec(
                                type=ComponentType.CODE_TERMINAL,
                                slot=SemanticSlot.HERO_CARD,
                                props={"title": "system.sh", "lines": ["$ system --status", "[✓] Status: RECOVERED"]}
                            ),
                            ComponentSpec(
                                type=ComponentType.KINETIC_HEADLINE,
                                slot=SemanticSlot.TICKER_BOTTOM,
                                props={"text": raw_dict.get("title", "RECOVERED"), "highlight_words": []}
                            )
                        ]
                    )
                ]
            )
