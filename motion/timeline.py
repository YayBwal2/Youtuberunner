from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from motion.schema import Storyboard, SceneSpec, ComponentSpec
from motion.easing import get_easing, interpolate


@dataclass
class TimelineComponent:
    spec: ComponentSpec
    scene_start: float
    scene_end: float

    def get_motion_state(self, global_t: float) -> Dict[str, Any]:
        """
        Calculates animated properties (opacity, translate_x, translate_y, scale, is_visible)
        at a specific timestamp, supporting both entrance and exit animation lifecycles.
        """
        local_t = global_t - self.scene_start
        scene_dur = max(0.1, self.scene_end - self.scene_start)
        motion = self.spec.motion
        delay = motion.delay
        dur = max(0.01, motion.duration)

        # Before entrance delay
        if local_t < delay:
            return {
                "opacity": 0.0,
                "translate_x": 0.0,
                "translate_y": 50.0,
                "scale": 0.92,
                "is_visible": False,
                "progress": 0.0
            }

        # Time remaining in scene (for exit animation)
        time_to_scene_end = self.scene_end - global_t
        exit_dur = 0.25

        # Check exit animation phase
        if motion.exit != "none" and time_to_scene_end < exit_dur and time_to_scene_end >= 0.0:
            exit_progress = max(0.0, min(1.0, 1.0 - (time_to_scene_end / exit_dur)))
            exit_eased = get_easing("ease_out_cubic")(exit_progress)
            
            if motion.exit == "fade_out":
                return {
                    "opacity": max(0.0, 1.0 - exit_eased),
                    "translate_x": 0.0,
                    "translate_y": 0.0,
                    "scale": 1.0,
                    "is_visible": exit_eased < 1.0,
                    "progress": 1.0
                }
            elif motion.exit == "fade_slide_down":
                return {
                    "opacity": max(0.0, 1.0 - exit_eased),
                    "translate_x": 0.0,
                    "translate_y": 40.0 * exit_eased,
                    "scale": 1.0 - 0.05 * exit_eased,
                    "is_visible": exit_eased < 1.0,
                    "progress": 1.0
                }

        # Entrance animation phase
        progress = max(0.0, min(1.0, (local_t - delay) / dur))
        easing_fn = get_easing(motion.easing)
        eased = easing_fn(progress)

        preset = motion.enter.lower()
        if preset == "spring_pop_in":
            scale = 0.90 + 0.10 * eased
            trans_y = 60.0 * (1.0 - eased)
            opacity = min(1.0, eased * 1.5)
        elif preset == "mask_reveal_up":
            scale = 1.0
            trans_y = 40.0 * (1.0 - eased)
            opacity = min(1.0, eased * 1.2)
        elif preset == "fade_slide_up":
            scale = 1.0
            trans_y = 50.0 * (1.0 - eased)
            opacity = eased
        elif preset == "diagram_grow":
            scale = 0.85 + 0.15 * eased
            trans_y = 20.0 * (1.0 - eased)
            opacity = eased
        else:
            scale = 1.0
            trans_y = 0.0
            opacity = eased

        return {
            "opacity": max(0.0, min(1.0, opacity)),
            "translate_x": 0.0,
            "translate_y": trans_y,
            "scale": scale,
            "is_visible": True,
            "progress": eased
        }


@dataclass
class TimelineScene:
    spec: SceneSpec
    start_time: float
    end_time: float
    duration: float
    components: List[TimelineComponent] = field(default_factory=list)
    words: List[Dict[str, Any]] = field(default_factory=list)

    def is_active(self, t: float) -> bool:
        return self.start_time <= t <= self.end_time


class VoiceSceneMapper:
    """
    Decoupled Voice-to-Scene mapping layer.
    Maps edge-tts sentence and word boundaries onto Storyboard scene blocks,
    with pause-snapping to guarantee scene cuts never split spoken words.
    """
    @staticmethod
    def _snap_to_nearest_pause(
        target_t: float,
        words: List[Dict[str, Any]],
        window: float = 0.75
    ) -> float:
        """
        Finds the nearest word silence boundary within window seconds of target_t.
        If target_t falls inside an active word, snaps to word['end'].
        """
        if not words:
            return target_t

        for i, w in enumerate(words):
            # If target_t falls inside this word, cut right after the word
            if w["start"] <= target_t <= w["end"]:
                return round(w["end"] + 0.02, 3)

            # If between this word and next word (a natural breath pause)
            if i < len(words) - 1:
                next_w = words[i + 1]
                if w["end"] <= target_t <= next_w["start"]:
                    return round(target_t, 3)

        return round(target_t, 3)

    @classmethod
    def map_storyboard_to_voice(
        cls,
        storyboard: Storyboard,
        voice_data: Dict[str, Any]
    ) -> List[TimelineScene]:
        sentences = voice_data.get("sentences", [])
        all_words = voice_data.get("words", [])
        total_audio_duration = voice_data.get("duration", 0.0)

        num_scenes = len(storyboard.scenes)
        if num_scenes == 0:
            return []

        timeline_scenes: List[TimelineScene] = []

        # Case 1: Audio sentences match scene count 1:1
        if len(sentences) == num_scenes:
            for idx, scene_spec in enumerate(storyboard.scenes):
                s_info = sentences[idx]
                start = s_info["start"]
                end = s_info["end"]
                
                # Snap end boundary to word pause
                if idx < num_scenes - 1:
                    end = cls._snap_to_nearest_pause(end, all_words)

                scene_words = [w for w in all_words if start <= w["start"] <= end + 0.05]
                
                t_scene = TimelineScene(
                    spec=scene_spec,
                    start_time=start,
                    end_time=end,
                    duration=max(0.1, end - start),
                    words=scene_words
                )
                t_scene.components = [
                    TimelineComponent(spec=c, scene_start=start, scene_end=end)
                    for c in scene_spec.components
                ]
                timeline_scenes.append(t_scene)

        # Case 2: Proportional mapping with natural speech pause snapping
        else:
            time_per_scene = total_audio_duration / num_scenes
            prev_end = 0.0

            for idx, scene_spec in enumerate(storyboard.scenes):
                start = prev_end
                if idx == num_scenes - 1:
                    end = total_audio_duration
                else:
                    raw_end = (idx + 1) * time_per_scene
                    end = cls._snap_to_nearest_pause(raw_end, all_words)
                    # Guard minimum scene duration
                    if end - start < 0.8:
                        end = start + 0.8

                prev_end = end
                scene_words = [w for w in all_words if start <= w["start"] <= end + 0.05]

                t_scene = TimelineScene(
                    spec=scene_spec,
                    start_time=round(start, 3),
                    end_time=round(end, 3),
                    duration=max(0.1, round(end - start, 3)),
                    words=scene_words
                )
                t_scene.components = [
                    TimelineComponent(spec=c, scene_start=round(start, 3), scene_end=round(end, 3))
                    for c in scene_spec.components
                ]
                timeline_scenes.append(t_scene)

        return timeline_scenes


class TimelineEngine:
    """
    Global timeline query engine for frame-accurate playback state.
    """
    def __init__(self, scenes: List[TimelineScene]):
        self.scenes = scenes
        self.total_duration = scenes[-1].end_time if scenes else 0.0

    def get_active_scene(self, t: float) -> Optional[TimelineScene]:
        for scene in self.scenes:
            if scene.is_active(t):
                return scene
        return self.scenes[-1] if self.scenes else None
