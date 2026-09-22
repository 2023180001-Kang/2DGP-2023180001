# 실습 과제 진행
from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.01)
    

def move_circle():
    for degree in range(361):
        theta = math.radians(degree)
        x = 400 + 200 * math.cos(theta)
        y = 300 + 200 * math.sin(theta)

        draw_character(x, y)
    

def move_top():
    x = 200
    y = 300
    for plus in range(201):
        clear_canvas()

        current_y = y + plus
        draw_character(x, current_y)
    return x, current_y


def move_right(x, y):
    for plus in range(401):
        clear_canvas()

        current_x = x + plus
        draw_character(current_x, y)
    return current_x, y


def move_bottom(x1, y1):
    for minus in range(201):
        clear_canvas()

        current_y = y1 - minus
        draw_character(x1, current_y)
    return x1, current_y


def move_left(x2, y2):
    for minus in range(401):
        clear_canvas()
        current_x = x2 - minus
        draw_character(current_x, y2)


def move_rectangle():
    x, y = move_top()
    x1, y1 = move_right(x, y)
    x2, y2 = move_bottom(x1, y1)
    move_left(x2, y2)
    

def moveA_TO_B():
    x = 100
    y = 100

    for plus in range(601):

        current_x = x + plus

        draw_character(current_x, y)

    return current_x, y

def moveB_TO_C(x, y):
    for step in range(401):
        t = step/400

        current_x = x - 300 * t
        current_y = y + 400 * t

        draw_character(current_x, current_y)

    return current_x, current_y
    

def moveC_TO_A(x, y):
    for step in range(401):
        t = step/400

        current_x = x - 300 * t
        current_y = y - 400 * t

        draw_character(current_x, current_y)
    return current_x, current_y
    

def move_triangle():
    x, y = moveA_TO_B()
    x, y = moveB_TO_C(x, y)
    x, y = moveC_TO_A(x, y)
    

while True:
    move_circle()
    move_rectangle()
    move_triangle()
   

    # break


close_canvas()