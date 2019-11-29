from world import World
import pygame
import time
import utils

class Simulator:
    def __init__(self, space_shape, batch_size, agent_size, ntargets, nwalls, rendering):
        self.__world = World(space_shape, batch_size,
                            agent_size, ntargets,
                            nwalls)

        self.__rendering = rendering
        self.__render_space_shape = (1000, 1000)

        self.__w = space_shape[1]
        self.__h = space_shape[0]
        #How much is the step in the render space
        self.__dw = self.__render_space_shape[0]/space_shape[1]
        self.__dh = self.__render_space_shape[1]/space_shape[0]
    
        self.__screen = pygame.display.set_mode(self.__render_space_shape)


    def render(self):
        if self.__rendering:
            self.__screen.fill(utils.BG)
            for x in range(self.__w):
                for y in range(self.__h):
                    # Draw walls
                    if self.__world.map[x, y] == utils.WALL:
                        rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                            int(self.__dw), int(self.__dh))
                        pygame.draw.rect(self.__screen, utils.WALL_COLOR, rect)

                    # Draw targets
                    if self.__world.map[x, y] == utils.TARGET:
                        rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                            int(self.__dw), int(self.__dh))
                        pygame.draw.rect(self.__screen, utils.TARGET_COLOR, rect)

                    # Draw agents
                    if self.__world.agent_layer[x, y] == 1:
                        rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                            int(self.__dw), int(self.__dh))
                        pygame.draw.rect(self.__screen, utils.AGENT_COLOR, rect)


            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return True

            pygame.display.update()
