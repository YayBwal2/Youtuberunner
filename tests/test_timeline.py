import unittest
from motion.schema import Storyboard, SceneSpec, ComponentSpec, ComponentType, MotionSpec
from motion.timeline import TimelineComponent, VoiceSceneMapper, TimelineEngine


class TestTimeline(unittest.TestCase):
    def test_timeline_component_lifecycle(self):
        """Verify component state transitions across delay, entrance, hold, and exit."""
        spec = ComponentSpec(
            type=ComponentType.CODE_TERMINAL,
            motion=MotionSpec(
                enter="spring_pop_in",
                exit="fade_out",
                delay=0.5,
                duration=0.5,
                easing="spring"
            )
        )
        t_comp = TimelineComponent(spec=spec, scene_start=2.0, scene_end=5.0)

        # 1. Before entrance delay (t = 2.2, local_t = 0.2 < delay 0.5)
        st_early = t_comp.get_motion_state(2.2)
        self.assertFalse(st_early["is_visible"])
        self.assertEqual(st_early["opacity"], 0.0)

        # 2. Mid entrance (t = 2.75, local_t = 0.75, progress = 0.5)
        st_mid = t_comp.get_motion_state(2.75)
        self.assertTrue(st_mid["is_visible"])
        self.assertGreater(st_mid["opacity"], 0.0)
        self.assertLessEqual(st_mid["opacity"], 1.0)

        # 3. Fully rested state (t = 3.5)
        st_rest = t_comp.get_motion_state(3.5)
        self.assertTrue(st_rest["is_visible"])
        self.assertEqual(st_rest["opacity"], 1.0)
        self.assertLess(abs(st_rest["scale"] - 1.0), 0.01)

        # 4. Exit transition (scene ends at 5.0, so at t=4.9 exit is active)
        st_exit = t_comp.get_motion_state(4.9)
        self.assertLess(st_exit["opacity"], 1.0)

    def test_voice_scene_mapper_pause_snapping(self):
        """Verify that scene boundary snaps to natural silence gaps between words."""
        words = [
            {"word": "Nvidia", "start": 0.0, "end": 0.6},
            {"word": "Blackwell", "start": 0.7, "end": 1.4},
            # Gap between 1.4 and 1.8s
            {"word": "draws", "start": 1.8, "end": 2.2},
            {"word": "power", "start": 2.3, "end": 2.9}
        ]
        # If target is 1.5 (inside gap), should snap smoothly
        snapped = VoiceSceneMapper._snap_to_nearest_pause(1.5, words)
        self.assertEqual(snapped, 1.5)

        # If target is 0.3 (inside word 'Nvidia'), snap to 0.62 (after word)
        snapped_mid_word = VoiceSceneMapper._snap_to_nearest_pause(0.3, words)
        self.assertEqual(snapped_mid_word, 0.62)


if __name__ == "__main__":
    unittest.main()
