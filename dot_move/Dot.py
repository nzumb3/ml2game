import numpy as np


#GLOBAL CONSTANTS
MAX_SPEED = 5 #maximum allowed speed
BOUNDS = (640, 400) #bounds of the window

class Dot:

    def __init__(self, position, goal, parameters):
        self.speed = 0
        self.position = position
        self.goal = goal
        self.alive = True
        self.reward = 0
        self.parameters = parameters

    def get_position(self):
        return self.position

    def get_reward(self):
        return self.reward

    def get_parameters(self):
        return self.parameters

    def move(self, info):
        #param: info: contains surroundings data for computation of the next move
        if self.speed <= MAX_SPEED:
            self.speed += 1
        #rnd_angle = 2*np.pi*np.random.rand()
        rnd_angle = self.policy(info)
        new_pos = [
            int(self.position[0] + np.cos(rnd_angle)*self.speed),
            int(self.position[1] + np.sin(rnd_angle)*self.speed)
        ]
        self.position = new_pos
        self.check_position()
        self.reward -= 1
        return self.alive

    def check_position(self):
        if self.position[0] < 0:
            self.alive = False
            self.position[0] = 0
        if self.position[1] < 0:
            self.alive = False
            self.position[1] = 0
        if self.position[0] > BOUNDS[0]:
            self.alive = False
            self.position[0] = BOUNDS[0]
        if self.position[1] > BOUNDS[1]:
            self.alive = False
            self.position[1] = BOUNDS[1]
        if (self.position[0] >= self.goal[0]-6 and self.position[0] <= self.goal[0]+6) and (self.position[1] >= self.goal[1]-6 and self.position[1] <= self.goal[1]+6):
            self.alive = False
        if not self.alive:
            self.compute_reward()

    def compute_reward(self):
        diff = np.sqrt((self.goal[0]-self.position[0])**2 + (self.goal[1]-self.position[1])**2)
        self.reward += (500*(1/diff))

    def is_alive(self):
        return self.alive

    def policy(self, state):
        state = np.array(state).ravel()
        angle = np.dot(state, self.parameters)
        angle = angle % (2*np.pi)
        #angle = np.random.normal(loc=angle, scale=0.25)
        #angle = angle % (2*np.pi)
        return angle