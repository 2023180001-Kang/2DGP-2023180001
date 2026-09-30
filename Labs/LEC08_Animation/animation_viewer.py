from dataclasses import dataclass
from math import ceil
from pathlib import Path

import pico2d


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
ASSET_DIR = Path(__file__).resolve().parent
ATLAS_WIDTH = 198
ATLAS_HEIGHT = 384
CELL_WIDTH = 33
CELL_HEIGHT = 32


@dataclass(frozen=True)
class Frame:
    left: int
    top: int
    width: int
    height: int
    offset_x: float
    offset_y: float


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float


def atlas_animation(name, row, bounds, frame_seconds):
    # Trim transparent padding, but retain each pose's position in its cell.
    frames = tuple(
        Frame(
            column * CELL_WIDTH + left,
            row * CELL_HEIGHT + top,
            right - left,
            bottom - top,
            (left + right) / 2 - CELL_WIDTH / 2,
            19.5 - (top + bottom) / 2,
        )
        for column, (left, top, right, bottom) in enumerate(bounds)
    )
    return Animation(name, frames, frame_seconds)


# Temporary visual row mapping, not Aseprite tags. JSON loading comes later.
ANIMATIONS = (
    atlas_animation("Idle", 0, (
        (6, 10, 24, 32), (5, 11, 24, 32),
        (3, 12, 24, 32), (5, 11, 24, 32),
    ), 0.14),
    atlas_animation("Run", 1, (
        (6, 10, 24, 32), (5, 9, 25, 31), (6, 10, 24, 32),
        (7, 10, 25, 32), (8, 9, 25, 31), (7, 10, 25, 32),
    ), 0.10),
    atlas_animation("Jump", 5, (
        (4, 9, 27, 30), (5, 7, 26, 29),
    ), 0.16),
    atlas_animation("Attack", 3, (
        (6, 10, 24, 32), (8, 13, 28, 32), (8, 13, 28, 32),
    ), 0.12),
    atlas_animation("Roll", 9, (
        (8, 14, 25, 32), (7, 14, 25, 31),
        (8, 14, 25, 32), (7, 14, 25, 31),
    ), 0.10),
)

# Even the shortest pose occupies at least half the canvas height.
DISPLAY_SCALE = ceil(
    CANVAS_HEIGHT / 2
    / min(frame.height for animation in ANIMATIONS for frame in animation.frames)
)


def draw_frame(character, frame):
    character.clip_draw(
        frame.left, character.h - frame.top - frame.height,
        frame.width, frame.height,
        CANVAS_WIDTH / 2 + frame.offset_x * DISPLAY_SCALE,
        CANVAS_HEIGHT / 2 + frame.offset_y * DISPLAY_SCALE,
        frame.width * DISPLAY_SCALE, frame.height * DISPLAY_SCALE,
    )


def main():
    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        character = pico2d.load_image(str(ASSET_DIR / "atlas.png"))
        if (character.w, character.h) != (ATLAS_WIDTH, ATLAS_HEIGHT):
            raise ValueError("atlas.png must be 198 x 384 for the manual frame table")
        grass = pico2d.load_image(str(ASSET_DIR / "grass.png"))
        animation_index = 0
        frame_index = 0
        running = True

        while running:
            for event in pico2d.get_events():
                if event.type == pico2d.SDL_QUIT or (
                    event.type == pico2d.SDL_KEYDOWN
                    and event.key == pico2d.SDLK_ESCAPE
                ):
                    running = False
            if not running:
                break

            pico2d.clear_canvas()
            grass.draw(CANVAS_WIDTH // 2, 30)
            animation = ANIMATIONS[animation_index]
            draw_frame(character, animation.frames[frame_index])
            pico2d.update_canvas()
            pico2d.delay(animation.frame_seconds)
            frame_index += 1
            if frame_index == len(animation.frames):
                frame_index = 0
                animation_index = (animation_index + 1) % len(ANIMATIONS)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
