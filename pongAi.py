import pygame
import random
from enum import Enum
import numpy as np

pygame.init()

WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

paddleVel = 8

paddleHeight = 80
paddleWidth = 10


# enum class for direction
class Direction(Enum):
    STAY = 1
    UP = 2
    DOWN = 3


class Paddle:
    Color = white

    def __init__(self, x, y, height=paddleHeight, width=paddleWidth):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.height = height
        self.width = width
        self.direction = Direction.STAY
        self.score = 0

    def draw(self, win):
        pygame.draw.rect(win, self.Color, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        self.direction = direction
        if self.direction == Direction.UP:
            self.y -= paddleVel
        elif self.direction == Direction.DOWN:
            self.y += paddleVel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.score = 0


class Ball:
    Color = red
    vel = 5

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.vel
        self.y_vel = self.vel * random.randint(-1, 1)

    def draw(self, win):
        pygame.draw.circle(win, self.Color, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = self.vel * random.randint(-1, 1)
        self.x_vel *= -1


def handleCollision(ball, left_paddle, right_paddle):
    # Hits the top or bottom
    if ball.y - ball.radius <= 0:
        ball.y_vel *= -1
    elif ball.y + ball.radius >= HEIGHT:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if ball.x - ball.radius == left_paddle.x + left_paddle.width and (ball.y >= left_paddle.y) and ball.y <= (
                left_paddle.y + left_paddle.height):
            ball.x_vel *= -1
            difference = ball.y - left_paddle.y
            factor = difference / left_paddle.height
            middlePaddle = left_paddle.height // 2
            ball.y_vel = ball.vel * factor

            if difference < middlePaddle:
                if not ball.y_vel < 0:
                    ball.y_vel *= -1
            else:
                if not ball.y_vel > 0:
                    ball.y_vel *= -1
            return True
    else:
        if ball.x + ball.radius == right_paddle.x and (ball.y >= right_paddle.y) and ball.y <= (
                right_paddle.y + right_paddle.height):
            ball.x_vel *= -1
            difference = ball.y - right_paddle.y
            factor = difference / right_paddle.height
            middlePaddle = right_paddle.height // 2
            ball.y_vel = ball.vel * factor

            if difference < middlePaddle:
                if not ball.y_vel < 0:
                    ball.y_vel *= -1
            else:
                if not ball.y_vel > 0:
                    ball.y_vel *= -1
    return False


def paddleMovement(paddle1, action):
    # paddle 1 movement
    # [straight, up, down]
    clock_wise = [Direction.STAY, Direction.UP, Direction.DOWN]
    idx = clock_wise.index(Direction.STAY)
    if np.array_equal(action, [1, 0, 0]):
        new_dir = clock_wise[idx]  # no change
    elif np.array_equal(action, [0, 1, 0]):
        new_dir = clock_wise[1]  # UP
    else:  # [0, 0, 1]
        new_dir = clock_wise[2]  # Down

    paddle1_direction = new_dir
    if paddle1_direction == Direction.UP:
        if paddle1.y - paddleVel > 0:
            paddle1.move(paddle1_direction)
    elif paddle1_direction == Direction.DOWN:
        if paddle1.y + paddleHeight + paddleVel < HEIGHT:
            paddle1.move(paddle1_direction)


def myAiMovement(paddle2, ball):
    if paddle2.y + (paddleHeight // 2) > ball.y and paddle2.y - paddleVel > 0:
        paddle2.move(Direction.UP)
    elif paddle2.y + (paddleHeight // 2) < ball.y and paddle2.y + paddleVel + paddle2.height < HEIGHT:
        paddle2.move(Direction.DOWN)


def draw(paddle1, paddle2, ball):
    WIN.fill(black)
    paddle1.draw(WIN)
    paddle2.draw(WIN)
    ball.draw(WIN)
    pygame.display.update()


def reset(paddle, ball):
    paddle.reset()
    ball.reset()


def main(action, paddle1, ball, paddle2):
    clock = pygame.time.Clock()
    draw(paddle1, paddle2, ball)
    reward = 0
    game_over = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    paddleMovement(paddle1, action)
    myAiMovement(paddle2, ball)

    ball.move()
    if handleCollision(ball, paddle1, paddle2):
        paddle1.score += 1
        reward = 10

    # check if game over
    if ball.x < 0 or ball.x > WIDTH:
        game_over = True
        reward = -10
        return reward, game_over, paddle1.score
    clock.tick(60)
    return reward, game_over, paddle1.score
