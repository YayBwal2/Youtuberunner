import unittest
from motion.schema import (
    Storyboard,
    SceneSpec,
    ComponentSpec,
    ComponentType,
    SemanticSlot,
    MotionSpec,
    StoryboardValidationError,
    validate_storyboard
)


class TestSchema(unittest.TestCase):
    def test_valid_storyboard(self):
        """Valid dictionary matching 1.0.0 schema must parse successfully."""
        raw = {
            "schema_version": "1.0.0",
            "fps": 30,
            "canvas_profile": "9:16_1080x1920",
            "title": "Nvidia Blackwell 1200W",
            "scenes": [
                {
                    "scene_id": "scene_01",
                    "slot": "hero_card",
                    "visual_intent": "Show terminal code reveal",
                    "components": [
                        {
                            "type": "CodeTerminal",
                            "slot": "hero_card",
                            "props": {"title": "blackwell.py", "lines": ["power = 1200"]},
                            "motion": {
                                "enter": "spring_pop_in",
                                "exit": "none",
                                "delay": 0.0,
                                "duration": 0.6,
                                "easing": "spring",
                                "properties": ["opacity", "scale"],
                                "layer_order": 1
                            }
                        }
                    ]
                }
            ]
        }
        board = validate_storyboard(raw, strict=True)
        self.assertEqual(board.schema_version, "1.0.0")
        self.assertEqual(board.fps, 30)
        self.assertEqual(len(board.scenes), 1)
        self.assertEqual(board.scenes[0].components[0].type, ComponentType.CODE_TERMINAL)
        self.assertEqual(board.scenes[0].components[0].motion.properties, ["opacity", "scale"])

    def test_strict_rejects_unknown_component(self):
        """Strict mode must raise StoryboardValidationError when unknown component is encountered."""
        raw = {
            "schema_version": "1.0.0",
            "fps": 30,
            "canvas_profile": "9:16_1080x1920",
            "title": "Invalid Test",
            "scenes": [
                {
                    "scene_id": "scene_01",
                    "components": [
                        {
                            "type": "UnknownFloatingBalloon",
                            "props": {}
                        }
                    ]
                }
            ]
        }
        with self.assertRaises(StoryboardValidationError) as ctx:
            validate_storyboard(raw, strict=True)
        self.assertIn("Unknown ComponentType", str(ctx.exception))
        self.assertIn("UnknownFloatingBalloon", str(ctx.exception))

    def test_fallback_recovery_mode(self):
        """Non-strict mode must log warning and recover into a valid playable storyboard."""
        raw = {
            "schema_version": "1.0.0",
            "title": "Broken Input",
            "scenes": []  # Invalid (empty scenes list)
        }
        board = validate_storyboard(raw, strict=False)
        self.assertIsInstance(board, Storyboard)
        self.assertGreaterEqual(len(board.scenes), 1)
        self.assertEqual(board.scenes[0].components[0].type, ComponentType.CODE_TERMINAL)


if __name__ == "__main__":
    unittest.main()
