from pico2d import *

import math

open_canvas(800, 600)

# 여기를 채우시오.
grass = load_image('grass.png')
character = load_image('character.png')

# 위 왼쪽 아래로 이동하기
# 다른 방향으로 가려면 y가 필요한데....

# 근데 원은 어떻게 만들지???
# 원은 반지름이 필요하고...

delta = 20
degree = 0
r = 100

while  True:
    degree += delta
    radian = math.radians(degree)
    x = 400 + r * math.cos(radian)
    y = 300 + r * math.sin(radian)
    clear_canvas()
    grass.draw(400, 30)

    # x y를 원과 같이 연산하기

    character.draw(x, y)
    update_canvas()
    delay(0.1)


close_canvas()

