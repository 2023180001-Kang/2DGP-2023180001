import json
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, mock_open, patch

import animation_viewer as viewer


class AtlasTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image_path, cls.atlas_size, cls.animations = viewer.load_animations(
            viewer.ASSET_DIR / "foxy.json",
        )


class FrameTests(AtlasTestCase):
    def test_at_least_four_animations_with_different_frame_counts(self):
        self.assertGreaterEqual(len(self.animations), 4)
        self.assertGreater(len({len(a.frames) for a in self.animations}), 1)

    def test_frame_rectangles_stay_inside_atlas(self):
        for animation in self.animations:
            for frame in animation.frames:
                with self.subTest(animation=animation.name, frame=frame):
                    self.assertGreater(frame.width, 0)
                    self.assertGreater(frame.height, 0)
                    self.assertGreaterEqual(frame.left, 0)
                    self.assertGreaterEqual(frame.top, 0)
                    self.assertLessEqual(frame.left + frame.width, self.atlas_size[0])
                    self.assertLessEqual(frame.top + frame.height, self.atlas_size[1])

    def test_frame_is_enlarged_and_anchor_is_inside_viewport(self):
        scale = viewer.DISPLAY_SCALE
        for animation in self.animations:
            for frame in animation.frames:
                with self.subTest(animation=animation.name, frame=frame):
                    x = viewer.CHARACTER_X + frame.offset_x * scale
                    y = viewer.CHARACTER_Y + frame.offset_y * scale
                    self.assertGreaterEqual(frame.height * scale, viewer.CANVAS_HEIGHT / 2)
                    self.assertGreaterEqual(x, 0)
                    self.assertLessEqual(x, viewer.CANVAS_WIDTH)
                    self.assertGreaterEqual(y, 50)
                    self.assertLessEqual(y, 565)

    def test_draw_converts_top_left_to_pico2d_coordinates(self):
        character = Mock(h=self.atlas_size[1])
        frame = self.animations[1].frames[1]
        viewer.draw_frame(character, frame)
        character.clip_draw.assert_called_once_with(
            frame.left, self.atlas_size[1] - frame.top - frame.height,
            frame.width, frame.height,
            viewer.CHARACTER_X + frame.offset_x * viewer.DISPLAY_SCALE,
            viewer.CHARACTER_Y + frame.offset_y * viewer.DISPLAY_SCALE,
            frame.width * viewer.DISPLAY_SCALE, frame.height * viewer.DISPLAY_SCALE,
        )

    def test_known_foxy_opaque_bounds_do_not_overlap_hud(self):
        # Across all 36 PNG frames, visible pixels span cell rows 4 through 31.
        self.assertLess(viewer.CHARACTER_Y + (16 - 4) * viewer.DISPLAY_SCALE, 565)
        self.assertGreater(viewer.CHARACTER_Y + (16 - 32) * viewer.DISPLAY_SCALE, 49)


class JsonTests(AtlasTestCase):
    def setUp(self):
        with (viewer.ASSET_DIR / "foxy.json").open(encoding="utf-8") as source:
            self.data = json.load(source)
        self.record = next(iter(self.data["frames"].values()))

    def parse_export(self):
        with patch.object(Path, "open", mock_open(read_data=json.dumps(self.data))):
            return viewer.load_animations(Path("fixtures/foxy.json"))

    def test_loads_all_exported_tags_and_frame_counts(self):
        self.assertEqual(self.atlas_size, (198, 384))
        self.assertEqual([(a.name, len(a.frames)) for a in self.animations], [
            ("idle", 4), ("run", 6), ("climb", 4), ("crouch", 3),
            ("hurt", 2), ("jump", 2), ("Wall Grab", 2), ("Hurt2", 1),
            ("Dizzy", 6), ("Roll", 4), ("LookUp", 1), ("Victory", 1),
        ])
        self.assertEqual(sum(len(a.frames) for a in self.animations), 36)

    def test_uses_exported_frame_durations(self):
        durations = {
            animation.name: {frame.duration_ms for frame in animation.frames}
            for animation in self.animations
        }
        self.assertEqual(durations["idle"], {100})
        self.assertEqual(durations["hurt"], {60})
        self.assertEqual(durations["Dizzy"], {140})
        self.assertEqual(durations["Roll"], {70})

    def test_image_path_is_relative_to_json_not_working_directory(self):
        image_path, _, _ = self.parse_export()
        self.assertEqual(image_path, Path("fixtures/foxy.png"))

    def test_preserves_export_order_instead_of_sorting_filenames(self):
        records = list(self.data["frames"].items())
        self.data["frames"] = dict([records[1], records[0], *records[2:]])
        _, _, animations = self.parse_export()
        self.assertEqual(animations[0].frames[0].left, 33)
        self.assertEqual(animations[0].frames[1].left, 0)

    def test_trimmed_variable_size_frames_preserve_alignment(self):
        first, second = list(self.data["frames"].values())[:2]
        first.update({
            "trimmed": True,
            "frame": {"x": 3, "y": 4, "w": 11, "h": 15},
            "spriteSourceSize": {"x": 4, "y": 9, "w": 11, "h": 15},
        })
        second.update({
            "trimmed": True,
            "frame": {"x": 40, "y": 0, "w": 17, "h": 20},
            "spriteSourceSize": {"x": 2, "y": 4, "w": 17, "h": 20},
            "duration": 230,
        })
        _, _, animations = self.parse_export()
        self.assertEqual(animations[0].frames[0], viewer.Frame(3, 4, 11, 15, -7, -0.5, 100))
        self.assertEqual(animations[0].frames[1], viewer.Frame(40, 0, 17, 20, -6, 2, 230))

    def test_rejects_nonpositive_or_noninteger_duration(self):
        for duration in (0, -1, True, 100.5, "100"):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                self.record["duration"] = duration
                self.parse_export()

    def test_rejects_invalid_or_out_of_bounds_rectangles(self):
        original = dict(self.record["frame"])
        for key, value in (("x", -1), ("w", 0), ("h", -2), ("y", 384), ("w", True), ("x", 0.5)):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.record["frame"] = {**original, key: value}
                self.parse_export()

    def test_rejects_invalid_trimmed_source_alignment(self):
        original = dict(self.record["spriteSourceSize"])
        for key, value in (("x", -1), ("w", 32), ("x", 33), ("h", 0)):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.record["spriteSourceSize"] = {**original, key: value}
                self.parse_export()

    def test_rejects_invalid_tag_ranges_without_silent_clamping(self):
        tag = self.data["meta"]["frameTags"][0]
        for start, end in ((-1, 3), (0, 36), (2, 1), (True, 3), (0, 3.5)):
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                tag["from"], tag["to"] = start, end
                self.parse_export()

    def test_rejects_missing_animation_tags(self):
        self.data["meta"]["frameTags"] = []
        with self.assertRaises(ValueError):
            self.parse_export()

    def test_rejects_empty_frames_or_non_hash_format(self):
        for frames in ({}, []):
            with self.subTest(frames=frames), self.assertRaises(ValueError):
                self.data["frames"] = frames
                self.parse_export()

    def test_rejects_rotated_frames_explicitly(self):
        self.record["rotated"] = True
        with self.assertRaisesRegex(ValueError, "Rotated"):
            self.parse_export()

    def test_rejects_unsupported_tag_direction_explicitly(self):
        self.data["meta"]["frameTags"][0]["direction"] = "reverse"
        with self.assertRaisesRegex(ValueError, "direction"):
            self.parse_export()

    def test_rejects_invalid_atlas_size(self):
        for width, height in ((198, 0), (True, 384), (198, -1), (198.5, 384)):
            with self.subTest(width=width, height=height), self.assertRaises(ValueError):
                self.data["meta"]["size"] = {"w": width, "h": height}
                self.parse_export()

    def test_invalid_json_reports_decode_error(self):
        with patch.object(Path, "open", mock_open(read_data="{invalid")):
            with self.assertRaises(json.JSONDecodeError):
                viewer.load_animations("fixtures/foxy.json")


class PlaybackTests(AtlasTestCase):
    def setUp(self):
        self.player = viewer.Playback(self.animations)
        self.loop_ms = sum(frame.duration_ms for frame in self.player.animation.frames)

    def test_frame_keeps_its_full_duration(self):
        duration = self.player.frame.duration_ms
        self.player.update(duration - 1)
        self.assertEqual(self.player.frame_index, 0)
        self.player.update(1)
        self.assertEqual(self.player.frame_index, 1)

    def test_four_loops_do_not_start_pause(self):
        self.player.update(self.loop_ms * (viewer.REPEAT_COUNT - 1))
        self.assertEqual(self.player.completed_loops, 4)
        self.assertEqual(self.player.frame_index, 0)
        self.assertFalse(self.player.pausing)

    def test_fifth_loop_ends_on_last_frame_before_pause(self):
        self.player.update(self.loop_ms * viewer.REPEAT_COUNT - 1)
        self.assertFalse(self.player.pausing)
        self.player.update(1)
        self.assertTrue(self.player.pausing)
        self.assertEqual(self.player.completed_loops, 5)
        self.assertEqual(self.player.frame_index, len(self.player.animation.frames) - 1)
        self.assertEqual(self.player.elapsed_ms, 0)

    def test_pause_freezes_last_frame_for_one_second(self):
        self.player.update(self.loop_ms * viewer.REPEAT_COUNT)
        frozen = self.player.frame
        self.player.update(viewer.PAUSE_MS - 1)
        self.assertTrue(self.player.pausing)
        self.assertIs(self.player.frame, frozen)
        self.player.update(1)
        self.assertFalse(self.player.pausing)
        self.assertEqual(self.player.animation_index, 1)
        self.assertEqual(self.player.frame_index, 0)
        self.assertEqual(self.player.completed_loops, 0)

    def test_leftover_time_is_carried_into_next_animation(self):
        next_duration = self.animations[1].frames[0].duration_ms
        self.player.update(self.loop_ms * viewer.REPEAT_COUNT + viewer.PAUSE_MS + next_duration + 7)
        self.assertEqual(self.player.animation_index, 1)
        self.assertEqual(self.player.frame_index, 1)
        self.assertEqual(self.player.elapsed_ms, 7)

    def test_multiple_complete_sequences_return_to_first_frame(self):
        sequence_ms = sum(
            sum(f.duration_ms for f in a.frames) * viewer.REPEAT_COUNT + viewer.PAUSE_MS
            for a in self.animations
        )
        self.player.update(sequence_ms * 3)
        self.assertEqual(self.player, viewer.Playback(self.animations))

    def test_small_and_large_updates_produce_same_state(self):
        large_update = viewer.Playback(self.animations)
        large_update.update(19007)
        for _ in range(2715):
            self.player.update(7)
        self.player.update(2)
        self.assertEqual(self.player, large_update)

    def test_single_frame_animation_still_repeats_five_times(self):
        animation = viewer.Animation("Single", (replace(self.player.frame, duration_ms=70),))
        player = viewer.Playback((animation,))
        player.update(70 * viewer.REPEAT_COUNT)
        self.assertTrue(player.pausing)
        self.assertEqual(player.completed_loops, 5)
        player.update(viewer.PAUSE_MS)
        self.assertEqual(player, viewer.Playback((animation,)))

    def test_frames_in_same_animation_can_have_different_durations(self):
        frames = tuple(replace(self.player.frame, duration_ms=ms) for ms in (100, 230, 60))
        player = viewer.Playback((viewer.Animation("Mixed", frames),))
        player.update(100)
        self.assertEqual(player.frame_index, 1)
        player.update(229)
        self.assertEqual(player.frame_index, 1)
        player.update(1)
        self.assertEqual(player.frame_index, 2)
        player.update(60 + sum(f.duration_ms for f in frames) * 4)
        self.assertTrue(player.pausing)
        self.assertEqual(player.completed_loops, 5)

    def test_negative_elapsed_time_is_rejected(self):
        with self.assertRaises(ValueError):
            self.player.update(-1)


class WindowTests(AtlasTestCase):
    def test_escape_closes_canvas_without_drawing(self):
        escape = SimpleNamespace(type=viewer.pico2d.SDL_KEYDOWN, key=viewer.pico2d.SDLK_ESCAPE)
        library_path = viewer.pico2d.__file__
        with patch.object(viewer, "pico2d") as graphics:
            graphics.__file__ = library_path
            graphics.SDL_KEYDOWN = escape.type
            graphics.SDLK_ESCAPE = escape.key
            graphics.load_image.return_value = Mock(w=self.atlas_size[0], h=self.atlas_size[1])
            graphics.get_events.return_value = [escape]
            viewer.main()
            graphics.close_canvas.assert_called_once()
            graphics.load_image.return_value.clip_draw.assert_not_called()

    def test_quit_remains_responsive_during_pause(self):
        quit_event = SimpleNamespace(type=viewer.pico2d.SDL_QUIT)
        pause_time = sum(f.duration_ms for f in self.animations[0].frames) * viewer.REPEAT_COUNT
        library_path = viewer.pico2d.__file__
        with patch.object(viewer, "pico2d") as graphics, patch.object(
            viewer, "monotonic_ns", side_effect=[0, pause_time * 1_000_000],
        ), patch.object(viewer, "draw_status") as status:
            graphics.__file__ = library_path
            graphics.SDL_QUIT = quit_event.type
            graphics.load_image.return_value = Mock(w=self.atlas_size[0], h=self.atlas_size[1])
            graphics.get_events.side_effect = [[], [quit_event]]
            viewer.main()
            self.assertTrue(status.call_args.args[1].pausing)
            self.assertEqual(graphics.get_events.call_count, 2)
            graphics.close_canvas.assert_called_once()

    def test_asset_failure_still_closes_canvas(self):
        with patch.object(viewer, "pico2d") as graphics:
            graphics.load_image.side_effect = OSError("missing image")
            with self.assertRaises(OSError):
                viewer.main()
            graphics.close_canvas.assert_called_once()

    def test_mismatched_image_size_still_closes_canvas(self):
        with patch.object(viewer, "pico2d") as graphics:
            graphics.load_image.return_value = Mock(w=1, h=1)
            with self.assertRaisesRegex(ValueError, "Image size"):
                viewer.main()
            graphics.close_canvas.assert_called_once()

    def test_missing_json_does_not_open_canvas(self):
        with patch.object(viewer, "pico2d") as graphics, patch.object(
            viewer, "load_animations", side_effect=FileNotFoundError("foxy.json"),
        ):
            with self.assertRaises(FileNotFoundError):
                viewer.main()
            graphics.open_canvas.assert_not_called()


if __name__ == "__main__":
    unittest.main()
