from dataclasses import dataclass
import json
from pathlib import Path
from time import monotonic_ns

import pico2d


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
ASSET_DIR = Path(__file__).resolve().parent
REPEAT_COUNT = 5
PAUSE_MS = 1000
# The shortest visible Foxy pose is 17 pixels tall: 17 * 18 = 306.
DISPLAY_SCALE = 18
CHARACTER_X = CANVAS_WIDTH / 2
# Compensate for the empty space above Foxy in the original source cells.
CHARACTER_Y = CANVAS_HEIGHT / 2 + 3.5 * DISPLAY_SCALE


@dataclass(frozen=True)
class Frame:
    left: int
    top: int
    width: int
    height: int
    offset_x: float
    offset_y: float
    duration_ms: int


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]


def load_animations(json_path):
    json_path = Path(json_path)
    with json_path.open(encoding="utf-8") as source:
        data = json.load(source)

    meta = data["meta"]
    frames = []
    # Aseprite tag indices refer to the export order, not filename sorting.
    for record in data["frames"].values():
        if record["rotated"]:
            raise ValueError("Rotated atlas frames are not supported")
        if record["duration"] <= 0:
            raise ValueError("Frame duration must be positive")
        rect = record["frame"]
        sprite = record["spriteSourceSize"]
        original = record["sourceSize"]
        frames.append(Frame(
            rect["x"], rect["y"], rect["w"], rect["h"],
            sprite["x"] + rect["w"] / 2 - original["w"] / 2,
            original["h"] / 2 - sprite["y"] - rect["h"] / 2,
            record["duration"],
        ))

    animations = []
    for tag in meta["frameTags"]:
        if tag["direction"] != "forward":
            raise ValueError(f"Unsupported tag direction: {tag['direction']}")
        animation_frames = tuple(frames[tag["from"]:tag["to"] + 1])
        if not animation_frames:
            raise ValueError(f"Animation has no frames: {tag['name']}")
        animations.append(Animation(tag["name"], animation_frames))
    if not animations:
        raise ValueError("The atlas must contain animation tags")

    return (
        json_path.parent / meta["image"],
        (meta["size"]["w"], meta["size"]["h"]),
        tuple(animations),
    )


@dataclass
class Playback:
    animations: tuple[Animation, ...]
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
            duration = PAUSE_MS if self.pausing else self.frame.duration_ms
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
        CHARACTER_X + frame.offset_x * DISPLAY_SCALE,
        CHARACTER_Y + frame.offset_y * DISPLAY_SCALE,
        frame.width * DISPLAY_SCALE, frame.height * DISPLAY_SCALE,
    )


def draw_status(font, playback):
    pico2d.draw_rectangle(
        0, 565, CANVAS_WIDTH - 1, CANVAS_HEIGHT - 1,
        29, 47, 39, filled=True,
    )
    pico2d.draw_rectangle(
        0, 0, CANVAS_WIDTH - 1, 49, 29, 47, 39, filled=True,
    )
    color = (240, 245, 235)
    font.draw(24, 582, "FOXY / ANIMATION VIEWER", color)
    font.draw(
        480, 582,
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
    image_path, atlas_size, animations = load_animations(ASSET_DIR / "Foxy.json")
    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pico2d.hide_lattice()
        character = pico2d.load_image(str(image_path))
        if (character.w, character.h) != atlas_size:
            raise ValueError(f"Image size does not match JSON metadata: {image_path.name}")
        grass = pico2d.load_image(str(ASSET_DIR / "grass.png"))
        font = pico2d.load_font(
            str(Path(pico2d.__file__).resolve().parent / "data" / "ConsolaMalgun.ttf"), 20,
        )
        playback = Playback(animations)
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
