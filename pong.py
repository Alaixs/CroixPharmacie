# Use keys A/Q, P/M, U/I, X/C to control players

import math
import itertools
import pygame
import random
import sys

from pharmacontroller import PharmaScreen, PANEL_SIZE, SCREEN_SIZE

PADDLE_SIZE = 6
PADDLE_MOVE_SPEED = 0.9
INITIAL_BALL_SPEED = 0.6
N_PLAYERS = 4
BALL_RADIUS = 0.5
DIAMOND_SIZE = 4
WALL_OFFSET = 7
ACCEL_FACTOR = 1.1

PADDLE_POSITIONS = ((PANEL_SIZE, 0, True, 0, WALL_OFFSET),
                    (PANEL_SIZE, SCREEN_SIZE - 1, True, 0, -WALL_OFFSET),
                    (0, PANEL_SIZE, False, WALL_OFFSET, 0),
                    (SCREEN_SIZE - 1, PANEL_SIZE, False, -WALL_OFFSET, 0))


def ccw(A,B,C):
    return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

# Return true if line segments AB and CD intersect
def seg_intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def collide_ball_segment(ball, segment, perturb_if_collide=0.0, accel_if_collide=1.0, dt=1.0):
    ballpos, ballv, ballrad = ball
    sp1, sp2 = segment

    pertx = random.random() - 0.5
    perty = random.random() - 0.5
    
    perturb = pygame.Vector2(pertx, perty).normalize() * ballv.magnitude() * perturb_if_collide

    '''
    for pt in (sp1, sp2):
        if ballpos.distance_to(pt) < ballrad:
            corner2ball = ballpos - pt
            newv = corner2ball.normalize() * ballv.magnitude()
            return (ballpos, newv * accel_if_collide + perturb, ballrad)
    '''

    if seg_intersect(sp1, sp2, ballpos, ballpos + ballv * dt):
        seg_normal = (sp2 - sp1).rotate(90)
        newv = ballv.reflect(seg_normal)
        return (ballpos, newv * accel_if_collide + perturb, ballrad)

    return ball

def paddle_to_seg(paddle):
    r, c, is_vertical, paddle_size = paddle
    return (
        pygame.Vector2(c, r),
        pygame.Vector2(c + paddle_size * int(not is_vertical), r + paddle_size * int(is_vertical))
    )

def init_random_ball():
    vx = random.random() + 0.5 * (1 - 2 * random.getrandbits(1))
    vy = random.random() + 0.5 * (1 - 2 * random.getrandbits(1))
    ballv = pygame.Vector2(vx, vy).normalize() * INITIAL_BALL_SPEED

    ballpos = pygame.Vector2(
        random.randrange(PANEL_SIZE, 2 * PANEL_SIZE),
        random.randrange(PANEL_SIZE, 2 * PANEL_SIZE)
    )

    while (abs(ballpos.x - (SCREEN_SIZE - 1)/2) +
           abs(ballpos.y - (SCREEN_SIZE - 1)/2)) < DIAMOND_SIZE + 0.01:   
        ballpos = pygame.Vector2(
            random.randrange(PANEL_SIZE, 2 * PANEL_SIZE),
            random.randrange(PANEL_SIZE, 2 * PANEL_SIZE)
        )
    return (ballpos, ballv, BALL_RADIUS)
    
if __name__ == '__main__':
    pygame.init()
    screen = PharmaScreen(True)

    paddles = []
    for i in range(4):
        if i < N_PLAYERS:
            # Human player
            paddle_size = PADDLE_SIZE
            r, c, is_vertical, _, _ = PADDLE_POSITIONS[i]
            dr = dc = 0
        else:
            # Wall
            paddle_size = PANEL_SIZE
            r, c, is_vertical, dr, dc = PADDLE_POSITIONS[i]
        paddles.append([r+dr, c+dc, is_vertical, paddle_size])

    ball = init_random_ball()

    walls = [
        (
            pygame.Vector2(PANEL_SIZE - BALL_RADIUS, -BALL_RADIUS),
            pygame.Vector2(PANEL_SIZE - BALL_RADIUS, PANEL_SIZE - BALL_RADIUS)
        ),
        (
            pygame.Vector2(-BALL_RADIUS, PANEL_SIZE - BALL_RADIUS),
            pygame.Vector2(PANEL_SIZE - BALL_RADIUS, PANEL_SIZE - BALL_RADIUS)
        ),
        (
            pygame.Vector2(23.5, 23.5 - DIAMOND_SIZE),
            pygame.Vector2(23.5 - DIAMOND_SIZE, 23.5)
        )
    ]

    for _ in range(9):
            new_wall = []
            for i in range(2):
                src_pt = walls[-3][i]
                dst_pt = pygame.Vector2(3 * PANEL_SIZE - src_pt.y - 1,
                                        src_pt.x)
                new_wall.append(dst_pt)
            walls.append(tuple(new_wall))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pressed_keys = pygame.key.get_pressed()

        # LEFT
        if pressed_keys[pygame.K_a] and paddles[0][0] > PANEL_SIZE:
            paddles[0][0] -= PADDLE_MOVE_SPEED
        if pressed_keys[pygame.K_q] and paddles[0][0] + paddles[0][3] < 2 * PANEL_SIZE:
            paddles[0][0] += PADDLE_MOVE_SPEED

        # RIGHT
        if pressed_keys[pygame.K_p] and paddles[1][0] > PANEL_SIZE:
            paddles[1][0] -= PADDLE_MOVE_SPEED
        if pressed_keys[pygame.K_m] and paddles[1][0] + paddles[1][3] < 2 * PANEL_SIZE:
            paddles[1][0] += PADDLE_MOVE_SPEED

        # TOP
        if pressed_keys[pygame.K_u] and paddles[2][1] > PANEL_SIZE:
            paddles[2][1] -= PADDLE_MOVE_SPEED
        if pressed_keys[pygame.K_i] and paddles[2][1] + paddles[2][3] < 2 * PANEL_SIZE:
            paddles[2][1] += PADDLE_MOVE_SPEED

        # BOTTOM
        if pressed_keys[pygame.K_x] and paddles[3][1] > PANEL_SIZE:
            paddles[3][1] -= PADDLE_MOVE_SPEED
        if pressed_keys[pygame.K_c] and paddles[3][1] + paddles[3][3] < 2 * PANEL_SIZE:
            paddles[3][1] += PADDLE_MOVE_SPEED

        # Collisions
        for wall in walls:
            ball = collide_ball_segment(ball, wall)

        for paddle in paddles:
            ball = collide_ball_segment(ball,
                                        paddle_to_seg(paddle),
                                        perturb_if_collide=0.01,
                                        accel_if_collide=ACCEL_FACTOR)

        ballpos, ballv, ballrad = ball
        ballpos += ballv
        ball = (ballpos, ballv, ballrad)

        if (ballpos.x < 0 or ballpos.y < 0 or ballpos.x > 3 * PANEL_SIZE -1 or ballpos.y > 3 * PANEL_SIZE -1):
            ball = init_random_ball()
            ballpos, ballv, ballrad = ball


        image = [[0. for c in range(SCREEN_SIZE)] for r in range(SCREEN_SIZE)]

        for paddle_r, paddle_c, is_vertical, size in paddles:
            dr, dc = (1, 0) if is_vertical else (0, 1)
            for i in range(size):
                image[round(paddle_r) + dr * i][round(paddle_c) + dc * i] = 1.0



        base_x = int(ballpos.x)
        base_y = int(ballpos.y)
        for dx in (0, 1):
            for dy in (0, 1):
                dst = math.dist((ballpos.x, ballpos.y), (base_x + dx, base_y + dy))
                # dst = 0 : max
                # dst = 1.4 : min
                val = 1.5 - dst
                image[base_y + dy][base_x + dx] = min(1.0, max(0.0, val))

        for x, y in itertools.product(range(SCREEN_SIZE), repeat=2):
            if abs(x - (SCREEN_SIZE - 1)/2) + abs(y - (SCREEN_SIZE - 1)/2) < DIAMOND_SIZE + 0.01:
                image[y][x] = 1.0
        screen.set_image(image)

    pygame.quit()
