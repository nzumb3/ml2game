from helper.FeatureFunctions import polynomial_features
from helper.LinearActionValueFunction import LinearActionValueFunction
from infinity_jump import infinity_jump
from rl_algorithms.Sarsa import Sarsa
import numpy as np

parameter_shape = (2,3)
action_function = LinearActionValueFunction(parameter_shape)
feature_args = {"degree":2, "interaction":False}
sarsa = Sarsa(action_function, polynomial_features, feature_args)