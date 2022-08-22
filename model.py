import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, inputSize, hiddenSize, outputSize):
        super(Linear_QNet, self).__init__()
        self.linear1 = nn.Linear(inputSize, hiddenSize)
        self.linear2 = nn.Linear(hiddenSize, outputSize)

    def forward(self, X):
        X = self.linear1(X)
        X = F.relu(X)
        X = self.linear2(X)
        return X

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.optimizer = torch.optim.Adam(model.parameters(), lr)
        #Mean squared error
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, game_over):
        # convert to tensors
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            action = torch.unsqueeze(action, 0)
            next_state = torch.unsqueeze(next_state, 0)
            reward = torch.unsqueeze(reward, 0)
            #convert to a tuple
            game_over = (game_over, )
        # predict value with current state
        pred = self.model(state)
        # r + y * max(next_predicted)
        #preds[argmax(action)] = Q_new
        target = pred.clone()

        for idx in range(len(game_over)):
            Q_new = reward[idx]
            if not game_over[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action).item()] = Q_new

        # empty out gradients
        self.optimizer.zero_grad()
        # calculate loss
        loss = self.criterion(target, pred)
        # calc gradients
        loss.backward()
        #optimize parameters
        self.optimizer.step()






