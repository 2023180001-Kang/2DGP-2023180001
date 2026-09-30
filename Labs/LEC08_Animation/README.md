# Drill 8: Foxy Animation Viewer

Run these commands from the repository root:

```powershell
python -m pip install -r Labs/LEC08_Animation/requirements.txt
python Labs/LEC08_Animation/animation_viewer.py
```

Press Escape or close the window to exit, including during the one-second pause.
Assets are resolved relative to the Python file, not the terminal's working directory.

## Assignment Requirements

- Source: `animation_viewer.py` in the existing `LEC08_Animation` lab folder.
- Assets: `foxy.png`, `foxy.json`, and `grass.png`. `Foxy.ase` is retained as editable source and is not parsed at runtime.
- Twelve animation types are loaded from the JSON export, including nine multi-frame animations.
- Characters stay in the center area of an 800 x 600 window, without moving across the screen.
- A common 18x scale preserves proportions and source alignment. Visible poses range from 306 to 504 pixels tall, meeting the half-screen-height requirement.
- Each animation plays five complete loops, freezes on its last frame for 1,000 ms, and advances to the next JSON tag.
- After the last animation, the sequence restarts indefinitely. One complete sequence takes 30.2 seconds.
- A monotonic clock and leftover-time accumulation keep frame timing independent of rendering speed.
- The HUD displays the current animation, frame, repeat count, and remaining pause time.

## JSON Animations

| Tag | Frames | Duration Per Frame |
| --- | ---: | ---: |
| idle | 4 | 100 ms |
| run | 6 | 100 ms |
| climb | 4 | 100 ms |
| crouch | 3 | 100 ms |
| hurt | 2 | 60 ms |
| jump | 2 | 100 ms |
| Wall Grab | 2 | 100 ms |
| Hurt2 | 1 | 100 ms |
| Dizzy | 6 | 140 ms |
| Roll | 4 | 70 ms |
| LookUp | 1 | 100 ms |
| Victory | 1 | 100 ms |

`load_animations()` reads Aseprite's **JSON Hash** export:

- `meta.image` chooses the image relative to the JSON file.
- `meta.size` is checked against the loaded image.
- `frameTags` supplies names and inclusive frame ranges, using the JSON frame export order.
- Each frame uses its own `frame.x/y/w/h` and `duration`; no fixed grid or frame count is required.
- `spriteSourceSize` and `sourceSize` preserve the original anchor when transparent borders are trimmed.
- JSON top-left coordinates are converted to pico2d bottom-left coordinates when drawing.
- Invalid sizes, coordinates, durations, and tag ranges are rejected. Rotated frames and non-forward tag directions are explicitly unsupported by this viewer.

## Bonus Support

Different animation frame counts are implemented and used: the provided export has 1, 2, 3, 4, and 6-frame animations. Mention this support in the assignment submission.

Variable-size and trimmed frames are also supported and tested. However, the supplied export uses uniform 33 x 32 source rectangles. Do not claim the complex-sheet usage bonus unless an actually variable-sized export is used for submission.

## Verification

```powershell
python -m unittest discover -s Labs/LEC08_Animation -p test_animation_viewer.py -v
```

Tests cover JSON tags and timing, variable-sized trimmed frames, coordinate conversion, five-loop and one-second-pause boundaries, single-frame animations, long frame delays, sequence wraparound, malformed metadata, Escape/window-close behavior, and canvas cleanup on errors.

## Development History

The original fourteen assignment commits were followed by seven actual development steps:

1. Foxy atlas assets, reliable paths, main entry point, and window cleanup.
2. Five temporary manual animation mappings with independent frame counts and enlarged rendering.
3. Time-based five-loop playback, one-second pauses, and infinite sequencing.
4. Playback HUD and background alignment.
5. Core automated tests and a pinned pico2d dependency.
6. Replacement of the manual table with Foxy PNG and JSON loading.
7. JSON validation, parser regression tests, lowercase `foxy.png`/`foxy.json` filenames, full-pose HUD alignment, and submission documentation.

The final viewer has no manual frame table or fallback to the old `atlas.png`.
