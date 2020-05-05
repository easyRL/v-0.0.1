import qTable

class QLearning(qTable.QTable):
    def __init__(self, action_size):
        super().__init__(action_size)

    def remember(self, state, action, reward, new_state, learning_rate, gamma):
        prevQValue = self.getQvalue(state, action)
        newQValue = self.getQvalue(new_state, self.choose_action(new_state))
        self.qtable[(state, action)] = prevQValue + learning_rate * (
                    reward + gamma * newQValue - prevQValue)

    def choose_action(self, state):
        q = [self.getQvalue(state, a) for a in range(self.action_size)]
        maxQ = max(q)
        return q.index(maxQ)

    def __deepcopy__(self, memodict={}):
        pass