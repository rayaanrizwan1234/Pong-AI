import torch
import random
import numpy as np
from pongAi import Paddle, Ball, main, Direction, paddleMovement, handleCollision, reset, myAiMovement
from collections import deque
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_0000
BATCH_SIZE = 100
LR = 0.001


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(5, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        # TODO: model, trainer

    def get_state(self, paddle, ball):
        # state has 5 values
        dir_s = paddle.direction == Direction.STAY
        dir_u = paddle.direction == Direction.UP
        dir_d = paddle.direction == Direction.DOWN

        state = [
            # directiom
            dir_s, dir_u, dir_d,
            # ball location
            ball.y < paddle.y,  # ball is up
            ball.y > paddle.y  # ball is down
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))  # popleft if exceed mem

    def train_long_memory(self):
        if len(self.memory) < BATCH_SIZE:
            # return a batch size list of tuples
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            # forward pass
            prediction = self.model(state0)
            # takes the largest value and put it as 1
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    record = 0
    agent = Agent()
    paddle = Paddle(20, 500 // 2 - (80 // 2))
    ball = Ball(700 // 2, 500 // 2, 10)
    paddle2 = Paddle(680 - 20, 500 // 2 - (80 // 2))
    while True:
        # get old sate
        state_old = agent.get_state(paddle, ball)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, game_over, score = main(final_move, paddle, ball, paddle2)
        myAiMovement(paddle2, ball)
        state_new = agent.get_state(paddle, ball)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        # remember
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory (replay memory)
            reset(paddle, ball)
            agent.n_games += 1

            if score > record:
                record = score
                #agent.model.save()

            print(f'Game {agent.n_games}, Score {score}, Record {record}')


if __name__ == "__main__":
    train()
