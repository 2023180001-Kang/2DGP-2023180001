# 실습 과제 진행
from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

def move_circle():
    print("circle")
    for degree in range(361):
        theta = math.radians(degree)
        x = 400 + 200 * math.cos(theta)
        y = 300 + 200 * math.sin(theta)
        # print("Theta:",theta)
        # print("X:", x)
        # print("Y:", y)
        clear_canvas()
        character.draw(x, y)
        update_canvas()
        delay(0.01)
    pass

def move_top():
    print("top")
    x = 200
    y = 300
    for plus in range(270):
        clear_canvas()

        current_y = y + plus
        character.draw(x, current_y)
        update_canvas()
        delay(0.01)
    return x, current_y


def move_right(x, y):
    print("right")
    for plus in range(401):
        clear_canvas()

        current_x = x + plus
        character.draw(current_x, y)
        print("current_x:", current_x)
        update_canvas()
        delay(0.01)
    return current_x, y


def move_bottom(x1, y1):
    print("bottom")
    for minus in range(301):
        clear_canvas()

        current_y = y1 - minus
        character.draw(x1, current_y)
        print("bottom y:", current_y)
        update_canvas()
        delay(0.01)


def move_left():
    print("left")
    
    # character.draw()


def move_rectangle():
    print("rectangle")
    x, y = move_top()
    x1, y1 = move_right(x, y)
    move_bottom(x1, y1)
    # move_left()
    pass

def move_triangle():
    print("triangle")
    pass

while True:
    move_circle()
    move_rectangle()
    # move_triangle()
    # pass

    # break


close_canvas()