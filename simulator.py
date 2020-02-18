from world import World
import gym
import utils
from ray.rllib.env import MultiAgentEnv
import gym
import numpy as np
import pygame

class Simulator(MultiAgentEnv):
    def __init__(self, env_config=None, space_shape=None,
                batch_size=None, agent_size=None,
                ntargets=None, nwalls=None,
                observation_range=None, stig_evaporation_speed=None,
                max_steps=None, rendering=False):
        
        if env_config != None:
            space_shape = env_config['space_shape']
            batch_size = env_config['batch_size']
            agent_size = env_config['agent_size']
            ntargets = env_config['ntargets']
            nwalls = env_config['nwalls']
            observation_range = env_config['observation_range']
            stig_evaporation_speed = env_config['stig_evaporation_speed']
            max_steps = env_config['max_steps']
            rendering = env_config['rendering']

        self.__world = World(space_shape, batch_size,
                            agent_size, ntargets,
                            nwalls, observation_range,
                            stig_evaporation_speed, max_steps)

        self.__max_steps = max_steps
        self.__steps = 0
        self.num_agents = batch_size
        self.n = self.num_agents

        self.__w = space_shape[1]
        self.__h = space_shape[0]
        self.__rendering = rendering
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(6, ((agent_size+2*observation_range)**2)))
        self.action_space = gym.spaces.Discrete(4)
        self.next_render = True

        if self.__rendering:
            import pygame
            self.__render_space_shape = (1000, 1000)
            #How much is the step in the render space
            self.__dw = self.__render_space_shape[0]/space_shape[1]
            self.__dh = self.__render_space_shape[1]/space_shape[0]

            self.__screen = pygame.display.set_mode(self.__render_space_shape)
            self.__base_layer = pygame.Surface(self.__render_space_shape)
            self.__overlay_obs = pygame.Surface(self.__render_space_shape)

            self.__overlay_stig = []
            for i in range(len(self.__world.stig_layers)):
                self.__overlay_stig.append(pygame.Surface(self.__render_space_shape, pygame.SRCALPHA))

            self.__overlay_obs.set_alpha(64)
            for layer in self.__overlay_stig:
                layer.set_alpha(128)
            
            self.__rend_blend = False
            self.setup_rend()

    def move(self):
        self.__world.move()

    def reset(self):
        return self.__world.reset()

    def step(self, actions):
        obss, rews, dones, _ = self.__world.step(actions)
        if self.__rendering:
            self.render()
            if dones['__all__']:
                self.next_render = True
        return obss, rews, dones, _

    def observe(self):
        return self.__world.observe()

    def get_agents(self):
        return self.__world.get_agents()

    def get_shadow(self, color, alpha):
        color.a = int(alpha)
        return color

    def setup_rend(self):
        self.__base_layer.fill(utils.BG)
        for x in range(self.__w):
            for y in range(self.__h):
                # Draw walls
                if self.__world.map[x, y, utils.WALL]:
                    rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                        int(self.__dw), int(self.__dh))
                    pygame.draw.rect(self.__base_layer, utils.WALL_COLOR, rect)

                # Draw targets
                if self.__world.map[x, y, utils.TARGET]:
                    rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                        int(self.__dw), int(self.__dh))
                    pygame.draw.rect(self.__base_layer, utils.TARGET_COLOR, rect)


    def render(self):
        if self.__rendering:
            if self.next_render == True:
                next_render = False
            self.setup_rend()

            self.__screen.blit(self.__base_layer, (0, 0))
            self.__overlay_obs.fill(utils.OVERLAY_OBS)
           
            if self.__rend_blend:
                for layer in self.__overlay_stig:
                    layer.fill(utils.EMPTY)
                for i, layer in enumerate(self.__world.stig_layers):
                    for x in range(self.__w):
                        for y in range(self.__h):
                            # Blit stig
                            if layer.value(x, y) != 0:
                                rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                                int(self.__dw), int(self.__dh))
                                pygame.draw.rect(self.__overlay_stig[i],
                                                self.get_shadow(layer.color, layer.value(x, y)),
                                                rect)
                for layer in self.__overlay_stig:
                    self.__screen.blit(layer, (0, 0))
          
            # Draw agents
            ## TODO: test if returning a custom struct instead of the whole agents is slower or not
            agents = self.__world.get_agents_obj()
            for agent in agents:
                x, y = agent.get_pos()
                size = agent.get_size()
                range_ = agent.get_obs_range()

                rect = pygame.Rect(int(self.__dw*(x-range_)), int(self.__dh*(y-range_)),
                                   int(self.__dw)*(2*range_+size), int(self.__dh)*(2*range_+size))
                self.__screen.blit(self.__overlay_obs, rect, area=rect)

                rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                   int(self.__dw)*size, int(self.__dh)*size)
                pygame.draw.rect(self.__screen, utils.AGENT_COLOR, rect)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return True
                    if event.key == pygame.K_s:
                        self.__rend_blend = not self.__rend_blend

            pygame.display.update()
