import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock, patch

import animation_viewer as viewer


class AtlasTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image_path, cls.atlas_size, cls.animations = viewer.load_animations(
            viewer.ASSET_DIR / "Foxy.json",
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


if __name__ == "__main__":
    unittest.main()
