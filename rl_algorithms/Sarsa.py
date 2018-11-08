import numpy as np

class Sarsa:

    def __init__(
            self,
            action_value_function,
            feature_function,
            feature_function_args,
            alpha = 10**(-2),
            epsilon = 0.1,
            gamma = 0.95
    ):
        self.action_value_function = action_value_function
        self.feature_function = feature_function
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.feature_function_args = feature_function_args

    def initialize(self, type):
        self.action_value_function.init_parameters(type)

    def take_action(self, state):
        state_features = self.feature_function(state,self.feature_function_args)
        action_values = self.action_value_function.get_action_values(state_features)
        return self.epsilon_greedy(action_values)

    def epsilon_greedy(self,action_values):
        greedy_prob = 1-self.epsilon
        rest_prob = self.epsilon/action_values.shape[0]
        rnd = np.random.rand()
        prob_val = 0
        action = 0
        for val in action_values:
            if val == np.max(action_values):
                prob_val += greedy_prob
            else:
                prob_val += rest_prob
            if rnd < prob_val:
                return action
            action += 1
        return action_values.shape[0]

    def update_parameters(self, states, actions, rewards):
        for i in range(len(states)-1):
            state, action, reward, new_state = states[i], actions[i], rewards[i], states[i+1]
            state_features = self.feature_function(state, self.feature_function_args)
            new_state_features = self.feature_function(new_state, self.feature_function_args)
            if i == len(states)-1:
                tmp = reward - self.action_value_function.get_action_value(state_features, action)
                tmp = self.alpha * tmp * self.action_value_function.get_action_value_derivative(state_features, action)
                self.action_value_function.parameter_update(tmp)
            else:
                next_action = self.take_action(new_state)
                tmp = reward + self.gamma*self.action_value_function.get_action_value(new_state_features, next_action) - self.action_value_function.get_action_value(state_features, action)
                tmp = self.alpha * tmp * self.action_value_function.get_action_value_derivative(state_features, action)
                self.action_value_function.parameter_update(tmp)