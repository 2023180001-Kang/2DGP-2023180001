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
    x = 600
    y = 200
    for plus in range(401):
        clear_canvas()

        current_y = y + plus
        character.draw(x, current_y)
        print("y:", current_y) 
        update_canvas()
        delay(0.01)



def move_right():
    print("right")
    x = 600
    y = 100
    for plus in range(400):
        clear_canvas()
        character.draw(x + plus, y)
        update_canvas()
        delay(0.01)


def move_bottom():
    print("bottom")
def move_left():
    print("left")
    
    # character.draw()


def move_rectangle():
    print("rectangle")
    move_top()
    # move_right()
    # move_bottom()
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