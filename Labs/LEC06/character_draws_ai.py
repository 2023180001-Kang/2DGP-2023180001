# 무한 반복 원-사각형-삼각형 그리기
import os
from pico2d import *
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
character = None


def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.01)


def draw_circle(cx=400, cy=300, radius=200):
    for degree in range(0, 361, 2):
        theta = math.radians(degree)
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        draw_character(x, y)


def draw_rectangle(x=180, y=120, width=440, height=360):
    for step in range(0, 101):
        t = step / 100
        left_top_x = x + width * t
        left_top_y = y + height
        draw_character(left_top_x, left_top_y)

    for step in range(0, 101):
        t = step / 100
        right_top_x = x + width
        right_top_y = y + height - height * t
        draw_character(right_top_x, right_top_y)

    for step in range(0, 101):
        t = step / 100
        bottom_right_x = x + width - width * t
        bottom_right_y = y
        draw_character(bottom_right_x, bottom_right_y)

    for step in range(0, 101):
        t = step / 100
        left_bottom_x = x
        left_bottom_y = y + height * t
        draw_character(left_bottom_x, left_bottom_y)


def draw_triangle(p1=(200, 500), p2=(400, 100), p3=(600, 500)):
    edges = [
        (p1, p2),
        (p2, p3),
        (p3, p1),
    ]

    for start, end in edges:
        sx, sy = start
        ex, ey = end
        steps = 100
        for step in range(0, steps + 1):
            t = step / steps
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            draw_character(x, y)


def run_animation(iterations=None):
    global character
    open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    character = load_image(os.path.join(BASE_DIR, 'character.png'))

    try:
        count = 0
        while True:
            draw_circle()
            draw_rectangle()
            draw_triangle()
            count += 1
            if iterations is not None and count >= iterations:
                break
    finally:
        close_canvas()


if __name__ == '__main__':
    run_animation()
