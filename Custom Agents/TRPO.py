from Agents import ppo, agent
from Agents.deepQ import DeepQ
import tensorflow as tf
#from tensorflow.linalg.experimental import conjugate_gradient
from scipy.stats import multimonial
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Conv2D
from tensorflow.keras.layers import Flatten, TimeDistributed, LSTM, multiply
from tensorflow.keras import utils
from tensorflow.keras.losses import KLDivergence
from tensorflow.keras.optimizers import Adam

import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from torch.optim import Adam
from torch.distributions import Categorical
from collections import namedtuple

class TRPO(ppo):
    displayName = 'TRPO Agent'
    #Invoke constructor
    def __init__(self, *args):
        paramLen = len(super().newParameters)
        super().__init__(*args[:-paramLen])
        self.Rollout = namedtuple('Rollout', '[states', 'actions', 'rewards', 'next_states',])
        self.rewards = []
        self.advantages = 0
    '''def optimize(self, action, state, policy, parameters, newParameters):
        advantage = 0
        for critic in range(10):
            for actor in range(10):
                # compute advantage
                advantage = 0
                super().updateActor()
            #optimize surrogate loss using recurrent neural network 
            parameters = newParameters
            super.updateCritic()'''
    
    def choose_action(self, state):
        qval = self.predict(state, False)
        epsilon = self.min_epsilon + (self.max_epsilon - self.min_epsilon) * np.exp(-self.decay_rate * self.time_steps)
        # TODO: Put epsilon at a level near this
        if random.random() > epsilon:
            action = np.argmax(qval)
        else:
            action = self.state_size.sample()
        return action

    '''def choose_action(self, state):
        observation = Tensor(state).unsqueeze(0)
        probabilities = super().criticModel(Variable(observation, requires_grad=True))
        action = probabilities.multimonial(1)
        return action, probabilities'''

    def train(num_rollouts=10):
        for epoch in range(super().epoch):
            rollouts = []

            for t in range(num_rollouts):
                DeepQ.reset()
                state = DeepQ.get_empty_state()
                done = False

                samples = []
                self.rewards = []
                while not done:
                    with torch.no_grad():
                        action = self.choose_action(state)
                        next_state, reward, done, _ = self.action(state)

                        samples.append((state, action, reward, next_state))

                        state = next_state
                
                states, actions, rewards, next_states = zip(*samples)

                states = torch.stack([torch.from_numpy(state) for state in states], dim=0).float())
                next_states = torch.stack([torch.from_numpy(state) for state in next_states], dim=0).float())
                actions = torch.as_tensor(actions).unsqueeze(1)
                rewards = torch.as_tensor(rewards).unsqueeze(1)

                rollouts.append(Rollout(states, actions, rewards, next_states))
        self.updateAgent(rollouts)

    max_d_kl = 0.01

    def get_action(self, state):
        state = torch.tensor(state).float().unsqueeze(0)
        dist = Categorical(super().actorModel(state))
        return dist.sample().item()

    def calculateTargetValues(self, mini_batch):
        pass

    def updateAgent(self, rollouts):
        states = torch.cat([r.states for r in rollouts], dim=0)
        actions = torch.cat([r.actions for r in rollouts], dim=0).flatten()

        self.advantages = [estimate_advantages(states, next_states[-1], rewards) for states, _, rewards, next_states in rollouts]
        self.advantages = torch.cat(self.advantages, dim=0).flatten()

        self.advantages = (self.advantages - self.advantages.mean()) / self.advantages.std()

        super().updateCritic(self.advantages)

        distribution = super().actorModel(states)

        distribution = torch.distributions.utils.clam_prob(distribution)

        probabilities = distribution[range(distribution.shape[0]), actions]

        self.L = surrogate_loss(probabilities, probabilities.detach(), self.advantages)
        self.KL = kl_div(distribution, distribution)

        self.g = flat_grad(L, self.parameters, retain_graph=True)
        self.d_kl = flat_grad(KL, self.parameters, create_graph=True)

        def HVP(v):
            return flat_grad(self.d_kl @ v, self.parameters, retain_graph=True)

        search_dir = conjugate_gradient(HVP, self.g)
        delta = 0.01
        max_length = torch.sqrt(2 * delta / (search_dir @ HVP(search_dir)))
        max_step = max_length * search_dir

        def criterion(step):
            apply_update(step)

            with torch.no_grad():
                distribution_new = super().actorModel(states)
                distribution_new = torch.distributions.utils.clam_probs(distribution_new)
                probabilities_new = distribution_new[range(distribution_new_shape[0]), actions]

                self.L_new = surrogate_loss(probabilities_new, probabilities, self.advantages)
                self.KL_new = kl_div(distribution, distribution_new)

            L_improvement = self.L_new - self.L_improvement
            if L_improvement > 0 and self.KL_new <= delta:
                return True
        
            apply_update(-step)
            return False

            i = 0
            while not criterion((0.9 ** i) * agent.max) and i < 10:
                i += 1

    def estimate_advantages(states, last_state, rewards):
        values = super().criticModel(states)
        last_value = critic(last_state.unsqueeze(0))
        next_values = torch.zeros_like(rewards)
        for i in reversed(range(rewards.shape[0])):
            last_value = next_values[i] = rewards[i] + 0.99 * last_value
        self.advantages = next_values - values
        return self.advantages

    def surrogate_loss(new_probabilities, old_probabilities):
        return (new_probabilities / old_probabilities * self.advantages).mean()

    def kl_div(p, q):
        p = p.detach()
        return (p * (p.log() - q.log())).sum(-1).mean()


    def flat_grad(y, x, retain_graph=False, create_graph=False):
        if create_graph:
            retain_graph = True

        g = torch.autograd.grad(y, x, retain_graph=retain_graph, create_graph=create_graph)
        g = torch.cat([t.view(-1) for t in g])
        return g

    def conjugate_gradient(A, b, delta=0., max_iterations=10):
    x = torch.zeros_like(b)
    r = b.clone()
    p = b.clone()

    i = 0
    while i < max_iterations:
        AVP = A(p)

        dot_old = r @ r
        alpha = dot_old / (p @ AVP)

        x_new = x + alpha * p

        if (x - x_new).norm() <= delta:
            return x_new

        i += 1
        r = r - alpha * AVP

        beta = (r @ r) / dot_old
        p = r + beta * p

        x = x_new
    return x


    def apply_update(grad_flattened):
        n = 0
        for p in actor.parameters():
            numel = p.numel()
            g = grad_flattened[n:n + numel].view(p.shape)
            p.data += g
            n += numel


    def remember(self, state, action, reward, new_state, done): 
        self.states.append(state)
        super().remember(action, state, reward, new_state, done)

    def reset(self):
        pass

    def __deepcopy__(self, memodict={}):
        pass

train(num_rollouts=10)