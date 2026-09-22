# 무한 반복 원-사각형-삼각형 그리기
from pico2d import *
import math

open_canvas(800, 600)
character = load_image('character.png')


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
    # top
    for step in range(0, 101):
        t = step / 100
        px = x + width * t
        py = y + height
        draw_character(px, py)

    # right
    for step in range(0, 101):
        t = step / 100
        px = x + width
        py = y + height - height * t
        draw_character(px, py)

    # bottom
    for step in range(0, 101):
        t = step / 100
        px = x + width - width * t
        py = y
        draw_character(px, py)

    # left
    for step in range(0, 101):
        t = step / 100
        px = x
        py = y + height * t
        draw_character(px, py)


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


while True:
    draw_circle()
    draw_rectangle()
    draw_triangle()

close_canvas()
