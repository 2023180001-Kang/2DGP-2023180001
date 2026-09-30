from pathlib import Path

import pico2d


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
ASSET_DIR = Path(__file__).resolve().parent


def main():
    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        character = pico2d.load_image(str(ASSET_DIR / "atlas.png"))
        grass = pico2d.load_image(str(ASSET_DIR / "grass.png"))
        frame = 0
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
            character.clip_draw(
                frame * 33, character.h - 32, 33, 32,
                CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
            )
            pico2d.update_canvas()
            frame = (frame + 1) % 4
            pico2d.delay(0.1)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
