# 실습 과제 진행
from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

def move_circle():
    print("circle")
    for degree in range(360):
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

def move_rectangle():
    print("rectangle")
    # move_top()
    # move_right()
    pass

def move_triangle():
    print("triangle")
    pass

while True:
    move_circle()
    # move_rectangle()
    # move_triangle()
    # pass

    # break


close_canvas()