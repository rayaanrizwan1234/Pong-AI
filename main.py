import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

paddleVel = 8


#enum class for direction
class Direction(Enum):
    UP = 1
    DOWN = 2


class Paddle:
    Color = white

    def __init__(self, x, y, height, width):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.height = height
        self.width = width

    def draw(self, win):
        pygame.draw.rect(win, self.Color, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        if direction == Direction.UP:
            self.y -= paddleVel
        elif direction == Direction.DOWN:
            self.y += paddleVel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball:
    Color = red
    vel = 7

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
                    ball.y_vel *=-1
    else:
        if ball.x + ball.radius == right_paddle.x and (ball.y >= right_paddle.y) and ball.y <= (
                right_paddle.y + right_paddle.height):
            ball.x_vel *= -1
            difference = ball.y - right_paddle.y
            factor = difference / right_paddle.height
            middlePaddle = right_paddle.height//2
            ball.y_vel = ball.vel * factor

            if difference < middlePaddle:
                if not ball.y_vel < 0:
                    ball.y_vel *= -1
            else:
                if not ball.y_vel > 0:
                    ball.y_vel *=-1


def paddleMovement(keyPressed, paddle1, paddle2):
    # paddle 1 up
    if keyPressed[pygame.K_w] and paddle1.y - paddleVel > 0:
        direction = Direction.UP
        paddle1.move(direction)
    # paddle 1 down
    if keyPressed[pygame.K_s] and paddle1.y + paddleVel + paddle1.height < HEIGHT:
        direction = Direction.DOWN
        paddle1.move(direction)
    # paddle 2 up
    if keyPressed[pygame.K_UP] and paddle2.y - paddleVel > 0:
        direction = Direction.UP
        paddle2.move(direction)
    # paddle 2 down
    if keyPressed[pygame.K_DOWN] and paddle2.y + paddleVel + paddle2.height < HEIGHT:
        direction = Direction.DOWN
        paddle2.move(direction)


def draw(paddle1, paddle2, ball):
    WIN.fill(black)
    paddle1.draw(WIN)
    paddle2.draw(WIN)
    ball.draw(WIN)
    pygame.display.update()


def main():
    run = True
    clock = pygame.time.Clock()
    paddleHeight = 80
    paddleWidth = 5
    paddle1 = Paddle(20, HEIGHT // 2 - (paddleHeight // 2), paddleHeight, paddleWidth)
    paddle2 = Paddle(680 - paddleWidth, HEIGHT // 2 - (paddleHeight // 2), paddleHeight, paddleWidth)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 10)
    while run:
        draw(paddle1, paddle2, ball)
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keyspressed = pygame.key.get_pressed()
        paddleMovement(keyspressed, paddle1, paddle2)

        ball.move()
        if ball.x < 0 or ball.x > WIDTH or ball.y < 0 or ball.y > HEIGHT:
            ball.reset()
        handleCollision(ball, paddle1, paddle2)


if __name__ == '__main__':
    main()
