import pygame
import numpy as np
from scipy.stats import multivariate_normal
import time

from Dot import Dot

class Dot_Move:

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 500 # added 100 pixel height for information
        self.fps = 40
        self.playtime = 0
        self.sense_range = 100
        self.num_senses = 8
        self.upper_level_mean = np.random.normal(size=self.num_senses*2+1)
        #self.upper_level_var = np.random.normal(size=self.num_senses*2+1)**2
        #self.upper_level_var = np.diag(self.upper_level_var)
        self.upper_level_var = np.identity(self.upper_level_mean.shape[0])
        self.decay = 0.95
        self.episode = 1
        self.dots_per_episode = 100
        self.alpha = 0.001
        self.avg_reward = 0

    def on_init(self):
        # initialize game and create window
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("mono", 20, bold=True)
        _, self.fh = self.font.size("h")

        self.dot_start_position = (int(self.width/2)-50, self.height-120)
        self.goal_position = (int(self.width/2), 20)
        self.sample_dots()

    def on_event(self, event):
        # event handling
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.playtime += self.clock.tick(self.fps) / 1000
        # define game loop here
        self.move_dots()
        if self.alive_dots == 0:
            self.update_upper_policy()
            self.sample_dots()
            time.sleep(0)

    def on_render(self):
        # use for render function calls
        self._display_surf.fill((255,255,255)) #creates white background

        #fill logic here
        self.draw_information_box()
        self.draw_goal()
        self.draw_dots()

        pygame.display.flip()

    def on_cleanup(self):
        # Called to save and exit game
        pygame.quit()

    def on_execute(self):
        # Call this function to start game
        if self.on_init() == False:
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


    ################# GAME LOGIC FUNCTIONS ################

    def move_dots(self):
        for dot in self.dots:
            if dot.is_alive():
                info = self.get_surroundings(dot.get_position())
                if not dot.move(info):
                    self.alive_dots -= 1

    def get_surroundings(self, position):
        senses = np.random.uniform(low=0,high=2*np.pi,size=self.num_senses)
        data = []
        for sense in senses:
            added = False
            for i in np.arange(10, self.sense_range+10, 10):
            #for i in range(1, self.sense_range+1):
                new_pos = [
                    int(position[0] + np.cos(sense)*i),
                    int(position[1] + np.sin(sense)*i)
                ]
                if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > self.width or new_pos[1] > self.width-100:
                    data.append(i)
                    data.append(0)
                    added = True
                    break
                elif new_pos[0] == self.goal_position[0] and new_pos[1] == self.goal_position[1]:
                    data.append(0)
                    data.append(i)
                    added = True
                    break
            if not added:
                data.append(0)
                data.append(0)
        data.append(1)
        return data

    def sample_dots(self):
        self.dots = []
        for _ in range(self.dots_per_episode):
            params = np.random.multivariate_normal(mean=self.upper_level_mean, cov=self.upper_level_var)
            self.dots.append(Dot(self.dot_start_position, self.goal_position, params))
        self.alive_dots = self.dots_per_episode
        self.episode += 1

    def collect_dataset(self):
        data = []
        for dot in self.dots:
            data.append([dot.get_parameters(), dot.get_reward()])
        return data

    def mean_derivative(self, sample):
        tmp = sample - self.upper_level_mean
        inv = np.linalg.solve(self.upper_level_var, np.identity(self.upper_level_mean.shape[0]))
        return np.dot(tmp.T, inv)

    def var_derivative(self, sample):
        tmp = (sample - self.upper_level_mean)**2
        inv1 = -np.linalg.solve(self.upper_level_var**2, np.identity(self.upper_level_var.shape[0]))
        inv2 = np.linalg.solve(self.upper_level_var**3, np.identity(self.upper_level_var.shape[0]))
        return inv1 + np.dot(tmp, inv2)

    def update_upper_policy(self):
        data = self.collect_dataset()
        mean_grad = np.zeros(shape=self.upper_level_mean.shape)
        var_grad = np.zeros(shape=self.upper_level_var.shape)
        self.avg_reward = 0
        for d in data:
            self.avg_reward += d[1]
            tmp = self.mean_derivative(d[0])*d[1]
            mean_grad += tmp
            tmp = self.var_derivative(d[0])*d[1]
            var_grad += tmp
        mean_grad *= 1/len(data)
        var_grad *= 1/len(data)
        self.avg_reward /= len(data)
        self.upper_level_mean += mean_grad*self.alpha
        self.upper_level_var *= self.decay
        print(np.diag(self.upper_level_var)[0])
        #self.upper_level_var += var_grad*self.alpha
        #self.upper_level_var = np.diag(np.diag(self.upper_level_var))

    ################# RENDER FUNCTIONS ###################

    def draw_information_box(self):
        pygame.draw.line(
            self._display_surf,
            (0, 0, 0),
            (0, self.height-100),
            (self.width, self.height-100)
        )
        text = "FPS: {}".format(
            np.round(self.clock.get_fps(), 1)
        )
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 0, 0))
        self._display_surf.blit(surface, ((self.width - fw - 5), (self.height-fh)))
        text = "Episode: {}  Alive: {}".format(self.episode, self.alive_dots)
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 0, 0))
        self._display_surf.blit(surface, (5, self.height - 100))
        text = "Avg Reward: {}".format(self.avg_reward)
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 0, 0))
        self._display_surf.blit(surface, (5, self.height - 100 + fh))

    def draw_goal(self):
        pygame.draw.circle(
            self._display_surf,
            (255, 0, 0),
            self.goal_position,
            6,
            0
        )

    def draw_dots(self):
        for dot in self.dots:
            pygame.draw.circle(
                self._display_surf,
                (0, 0, 0),
                dot.get_position(),
                4,
                0
            )

if __name__ == "__main__":
    #np.random.seed(12586777)
    test = Dot_Move()
    test.on_execute()