import pygame
import numpy as np

class App:

    def __init__(self, ai=False):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 400
        self.ai = ai

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("mono", 20, bold=True)
        _, self.fh = self.font.size("h")
        self.OBSTACLE_DICT = {
            1 : [1.0, 0, 0],
            2 : [0.95, 0.05, 0],
            3 : [0.85, 0.15, 0],
            4 : [0.75, 0.25, 0],
            5 : [0.65, 0.35, 0],
            6 : [0.55, 0.40, 0.05],
            7 : [0.45, 0.50, 0.05],
            8 : [0.35, 0.55, 0.10],
            9 : [0.25, 0.55, 0.20],
            10 : [0.15, 0.50, 0.35],
            11 : [0.05, 0.40, 0.55],
            12 : [0.01, 0.30, 0.69],
            "default" : [0.01, 0.20, 0.79]
        }
        self.fps = 35
        self.playtime = 0.0
        self.floor_height = int(self.height/2) + 100
        self.obstacles = []
        self.last_time = 0
        self.score = 0
        self.last_difficulty_change = 0
        self.difficulty = 1
        self.max_obstacles = 2
        self.move_speed = 2

        self.playerpos = [150, self.floor_height - 30, 20, 30] #x1, y1, width, height
        self.player_vert_movement = 0
        self.player_jumped = False
        self.thrusting = False
        self._lost = False

        self.place_obstacle()
        for _ in range(np.random.randint(low=25, high=50)):
            self.move_obstacles()
        self.place_obstacle()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self._lost:
                if not self.player_jumped:
                    self.thrusting = True
                    self.player_vert_movement -= 5
            if event.key == pygame.K_SPACE and self._lost:
                self.on_init()

    def on_loop(self):
        self.playtime += self.clock.tick(self.fps) / 1000
        if self.playtime - self.last_time > 1:
            self.last_time = self.playtime
            self.score += 1
        self.move_obstacles()
        self.move_player()
        self.place_obstacle()
        self.update_difficulty()
        if self.check_collision():
            self._lost = True

    def on_render(self):
        self._display_surf.fill((255,255,255))
        self.draw_top_frame()
        self.draw_top_frame_data()
        self.draw_floor()
        for obstacle in self.obstacles:
            self.draw_obstacle(obstacle[0])
        self.draw_player()
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            if not self._lost:
                for event in pygame.event.get():
                    self.on_event(event)
                self.on_loop()
                self.on_render()
            else:
                for event in pygame.event.get():
                    self.on_event(event)
                self.render_game_over()
        self.on_cleanup()

    ################# GAME LOGIC FUNCTIONS ################
    def move_obstacles(self):
        for obstacle in self.obstacles:
            obstacle[0][0] -= self.move_speed
            if obstacle[0][0] < -obstacle[0][2]:
                self.score += 10*obstacle[1]
                self.obstacles.remove(obstacle)

    def place_obstacle(self):
        if len(self.obstacles) < self.max_obstacles:
            rnd = np.random.rand()
            val = 0
            obs = 1
            if self.difficulty in self.OBSTACLE_DICT.keys():
                for i in range(3):
                    val += self.OBSTACLE_DICT[self.difficulty][i]
                    if rnd < val:
                        break
                    obs += 1
            else:
                for i in range(3):
                    val += self.OBSTACLE_DICT["default"][i]
                    if rnd < val:
                        break
                    obs += 1
            if len(self.obstacles) > 0 and self.obstacles[-1][0][0] > self.width -100:
                obstacle = [
                    np.random.randint(low=self.obstacles[-1][0][0] + 40, high=self.width + 300),  # x1
                    self.floor_height - 22 * obs,  # y1
                    int(12 * obs / 2),  # width
                    22 * obs  # height
                ]
            else:
                obstacle = [
                    np.random.randint(low=self.width - 100, high=self.width + 300),  # x1
                    self.floor_height - 22 * obs,  # y1
                    int(12 * obs / 2),  # width
                    22 * obs  # height
                ]
            self.obstacles.append([obstacle, obs])

    def update_difficulty(self):
        diff = self.score - self.last_difficulty_change
        if diff > 30 * self.difficulty:
            self.last_difficulty_change = self.score
            self.difficulty += 1
            if self.difficulty % 3 == 0:
                self.move_speed += 1
            if self.difficulty % 5 == 0:
                self.max_obstacles += 1

    def move_player(self):
        pressed_keys = pygame.key.get_pressed()
        if self.thrusting and pressed_keys[pygame.K_SPACE]:
            self.player_vert_movement -= 2
        else:
            self.thrusting = False
            self.player_jumped = True
        if self.player_vert_movement < -12:
            self.thrusting = False
            self.player_jumped = True
        if self.player_jumped or self.thrusting:
            self.playerpos[1] += self.player_vert_movement
            self.player_vert_movement += 1
        if self.playerpos[1] >= self.floor_height-30 and self.player_vert_movement > 0:
            self.playerpos[1] = self.floor_height-30
            self.player_vert_movement = 0
            self.player_jumped = False

    def check_collision(self):
        playerbox = [
            self.playerpos[0],
            self.playerpos[1]+self.playerpos[3],
            self.playerpos[0]+self.playerpos[2],
            self.playerpos[1]+self.playerpos[3]
        ]
        for obstacle in self.obstacles:
            obs_pos = [
                obstacle[0][0],
                obstacle[0][1],
                obstacle[0][0]+obstacle[0][2],
                obstacle[0][1]+obstacle[0][3],
            ]
            if (playerbox[0] > obs_pos[0] and playerbox[0] < obs_pos[2] and playerbox[1] <= obs_pos[3] and playerbox[1] >= obs_pos[1]) or (playerbox[2] > obs_pos[0] and playerbox[2] < obs_pos[2] and playerbox[3] <= obs_pos[3] and playerbox[3] >= obs_pos[1]):
                return True
        return False

    ################# DRAWING FUNCTIONS ###################
    def draw_top_frame_data(self):
        text = "FPS: {}".format(
            np.round(self.clock.get_fps(),1)
        )
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 0, 0))
        self._display_surf.blit(surface, ((self.width - fw - 10), (0)))
        text = "Score: {}     Difficulty: {}".format(
            self.score,
            self.difficulty
        )
        surface = self.font.render(text, True, (0, 0, 0))
        self._display_surf.blit(surface, (10, 0))

    def draw_top_frame(self):
        pygame.draw.line(
            self._display_surf,
            (0, 0, 0),
            (0, self.fh),
            (self.width, self.fh)
        )

    def draw_floor(self):
        pygame.draw.line(
            self._display_surf,
            (0, 0, 0),
            (0, self.floor_height),
            (self.width, self.floor_height)
        )

    def draw_obstacle(self, position):
        pygame.draw.rect(
            self._display_surf,
            (0, 0, 0),
            position
        )

    def draw_player(self):
        pygame.draw.rect(
            self._display_surf,
            (0, 0, 255),
            self.playerpos
        )

    def render_game_over(self):
        pygame.draw.rect(
            self._display_surf,
            (0, 0, 0),
            (10, 10, self.width-20, self.height-20)
        )
        text = "GAME OVER"
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (220, 0, 25))
        self._display_surf.blit(surface, (int(self.width / 2) - int(fw / 2), int(self.height / 2) - 100))

        text = "Press Space to continue"
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (200, 0, 50))
        self._display_surf.blit(surface, (int(self.width / 2) - int(fw / 2), int(self.height / 2) - 50))

        pygame.display.flip()