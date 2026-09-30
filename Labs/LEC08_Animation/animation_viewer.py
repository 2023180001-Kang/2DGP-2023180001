# 실습 과제 실행
from pico2d import *
import math

open_canvas(800, 600)

# 캐릭터 png를 추가
# 캐릭터 png 변경
character = load_image('SoldierMove.png')

# 바닥에 grass png를 추가
grass = load_image('grass.png')

# 캐릭터 4개 움직임 함수
def wallk_character():
    print("Wallk Character")
    pass

def run_character():
    print("Run Character")
    pass

def jump_character():
    print("Jump Character")
    pass

def attack_character():
    print("Attack Character")
    pass

# 첫 프레임 변수 선언
frame = 0

# 첫 이동을 위한 반복문 구현 시작
# 캐릭터 변경 후 사이즈 다시 100 100으로 변경
for x in range(0, 800, 5):
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 0, 100, 100, x, 90)
    update_canvas()
    frame = (frame + 1) % 8
    delay(0.05)
    pass


# while True:
    # clear_canvas()
    # wallk_character()
    # run_character()
    # jump_character()
    # attack_character()
    # update_canvas()
    # delay(0.01)



