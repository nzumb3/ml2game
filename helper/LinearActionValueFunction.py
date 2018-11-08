import numpy as np

class LinearActionValueFunction:

    def __init__(self, parameter_shape):
        self.parameter_shape = parameter_shape

    def init_parameters(self, type = "gaussian"):
        if type == "zero":
            self.theta = np.zeros(self.parameter_shape)
        elif type == "uniform":
            self.theta = np.random.uniform(low=-1,high=1,size=self.parameter_shape)
        elif type == "gaussian":
            self.theta = np.random.normal(size=self.parameter_shape)

    def get_action_values(self, state_features):
        action_values = np.dot(state_features, self.theta).ravel()
        return action_values

    def get_action_value(self, state_features, action):
        action_values = self.get_action_values(state_features)
        return action_values[action]

    def get_action_value_derivative(self, state_features, action):
        derivative = np.zeros(self.parameter_shape)
        derivative[:, action] += state_features.ravel()
        return derivative

    def parameter_update(self, update):
        self.theta += update