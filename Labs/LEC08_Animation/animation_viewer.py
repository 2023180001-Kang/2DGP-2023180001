from dataclasses import dataclass
from math import ceil
from pathlib import Path
from time import monotonic_ns

import pico2d


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
ASSET_DIR = Path(__file__).resolve().parent
ATLAS_WIDTH = 198
ATLAS_HEIGHT = 384
CELL_WIDTH = 33
CELL_HEIGHT = 32
REPEAT_COUNT = 5
PAUSE_MS = 1000


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
    frame_ms: int


def atlas_animation(name, row, bounds, frame_ms):
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
    return Animation(name, frames, frame_ms)


# Temporary visual row mapping, not Aseprite tags. JSON loading comes later.
ANIMATIONS = (
    atlas_animation("Idle", 0, (
        (6, 10, 24, 32), (5, 11, 24, 32),
        (3, 12, 24, 32), (5, 11, 24, 32),
    ), 140),
    atlas_animation("Run", 1, (
        (6, 10, 24, 32), (5, 9, 25, 31), (6, 10, 24, 32),
        (7, 10, 25, 32), (8, 9, 25, 31), (7, 10, 25, 32),
    ), 100),
    atlas_animation("Jump", 5, (
        (4, 9, 27, 30), (5, 7, 26, 29),
    ), 160),
    atlas_animation("Crouch", 3, (
        (6, 10, 24, 32), (8, 13, 28, 32), (8, 13, 28, 32),
    ), 120),
    atlas_animation("Roll", 9, (
        (8, 14, 25, 32), (7, 14, 25, 31),
        (8, 14, 25, 32), (7, 14, 25, 31),
    ), 100),
)

# Even the shortest pose occupies at least half the canvas height.
DISPLAY_SCALE = ceil(
    CANVAS_HEIGHT / 2
    / min(frame.height for animation in ANIMATIONS for frame in animation.frames)
)


@dataclass
class Playback:
    animations: tuple[Animation, ...] = ANIMATIONS
    animation_index: int = 0
    frame_index: int = 0
    completed_loops: int = 0
    elapsed_ms: float = 0
    pausing: bool = False

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, delta_ms):
        self.elapsed_ms += delta_ms
        # Keep leftover time across both frame and animation transitions.
        while True:
            duration = PAUSE_MS if self.pausing else self.animation.frame_ms
            if self.elapsed_ms < duration:
                break
            self.elapsed_ms -= duration

            if self.pausing:
                self.animation_index = (self.animation_index + 1) % len(self.animations)
                self.frame_index = 0
                self.completed_loops = 0
                self.pausing = False
            elif self.frame_index == len(self.animation.frames) - 1:
                self.completed_loops += 1
                if self.completed_loops == REPEAT_COUNT:
                    self.pausing = True
                else:
                    self.frame_index = 0
            else:
                self.frame_index += 1


def draw_frame(character, frame):
    character.clip_draw(
        frame.left, character.h - frame.top - frame.height,
        frame.width, frame.height,
        CANVAS_WIDTH / 2 + frame.offset_x * DISPLAY_SCALE,
        CANVAS_HEIGHT / 2 + frame.offset_y * DISPLAY_SCALE,
        frame.width * DISPLAY_SCALE, frame.height * DISPLAY_SCALE,
    )


def draw_status(font, playback):
    pico2d.draw_rectangle(
        0, 550, CANVAS_WIDTH - 1, CANVAS_HEIGHT - 1,
        29, 47, 39, filled=True,
    )
    pico2d.draw_rectangle(
        0, 0, CANVAS_WIDTH - 1, 49, 29, 47, 39, filled=True,
    )
    color = (240, 245, 235)
    font.draw(24, 575, "FOXY / ANIMATION VIEWER", color)
    font.draw(
        480, 575,
        f"{playback.animation.name} ({playback.animation_index + 1}/{len(playback.animations)})",
        color,
    )
    loop = min(playback.completed_loops + 1, REPEAT_COUNT)
    font.draw(
        24, 25,
        f"Loop {loop}/{REPEAT_COUNT}  Frame {playback.frame_index + 1}/{len(playback.animation.frames)}",
        color,
    )
    status = (
        f"Pause: {(PAUSE_MS - playback.elapsed_ms) / 1000:.1f}s"
        if playback.pausing else "Playing"
    )
    font.draw(360, 25, status, color)
    font.draw(660, 25, "ESC: Exit", color)


def main():
    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pico2d.hide_lattice()
        character = pico2d.load_image(str(ASSET_DIR / "atlas.png"))
        if (character.w, character.h) != (ATLAS_WIDTH, ATLAS_HEIGHT):
            raise ValueError("atlas.png must be 198 x 384 for the manual frame table")
        grass = pico2d.load_image(str(ASSET_DIR / "grass.png"))
        font = pico2d.load_font(
            str(Path(pico2d.__file__).resolve().parent / "data" / "ConsolaMalgun.ttf"), 20,
        )
        playback = Playback()
        previous_time = monotonic_ns()
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

            current_time = monotonic_ns()
            playback.update((current_time - previous_time) / 1_000_000)
            previous_time = current_time

            pico2d.clear_canvas()
            grass.draw(CANVAS_WIDTH // 2, 45, CANVAS_WIDTH, 62)
            draw_frame(character, playback.frame)
            draw_status(font, playback)
            pico2d.update_canvas()
            pico2d.delay(0.008)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
