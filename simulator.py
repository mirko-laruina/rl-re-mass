import pygame
from PIL import Image
import numpy as np
import time

BG = pygame.Color(15, 15, 15) #Black (but not too much)
TARGET_COLOR = pygame.Color(255, 255, 0) #Yellow
WALL_COLOR = pygame.Color(255, 0, 0)

WALL = 2
TARGET = 1



class Simulator:
    def __init__(self, space_shape, batch_size, agent_size, ntargets, nwalls, rendering):
        self.__render_space_shape = (1000, 1000)
        self.__batch_size = batch_size
        self.__agent_size = agent_size
        self.__ntargets = ntargets
        self.__nwalls = nwalls
        self.__rendering = rendering
        #Max/min wall length is a percentage of space height
        self.__max_wall_len = 0.7
        self.__min_wall_len = 0.3

        self.__w = space_shape[0]
        self.__h = space_shape[1]

        #How much is the step in the render space
        self.__dw = self.__render_space_shape[0]/self.__w
        self.__dh = self.__render_space_shape[1]/self.__h

        self.__screen = pygame.display.set_mode(self.__render_space_shape)
        self.__map = np.zeros((self.__w, self.__h))

        self.__generate_walls()
        self.__generate_targets()

    def __generate_walls(self):
        #We generate nwalls based on the x, with a random lenght
        #This has to be done BEFORE picking the targets
        #That's not the best method and it is NOT guarenteed to work
        #Can cycle forever
        #Ex. with high number of walls
        # THIS HAS TO BE EDITED
        i = 0
        while i < self.__nwalls:
            x = int(np.random.rand()*self.__w)
            if self.__map[x, 0] == WALL or self.__map[x, -1] == WALL:
                continue

            wall_lenght = np.random.rand()*self.__h*(self.__max_wall_len-self.__min_wall_len)
            wall_lenght += self.__min_wall_len*self.__h
            wall_lenght = int(wall_lenght)
            wall_arr = np.full(self.__h, False)
            wall_arr[:wall_lenght] = True
            reverse = np.random.rand() < 0.5
            self.__map[x, wall_arr if not reverse else ~wall_arr] = WALL

            #Check if a path is possible
            #Doesn't work properly
            sum = self.__map[x, wall_arr]
            if x != 0:
                sum += self.__map[x-1, wall_arr]
            if x != self.__w-1:
                sum += self.__map[x+1, wall_arr]
                
            sum = np.max(sum)
            if sum > WALL:
                self.__map[x, wall_arr if not reverse else ~wall_arr] = 0
                continue 

            i+=1

    def __generate_targets(self):
        #We pick ntargets points in the space
        self.__targets_mask = np.full((self.__w, self.__h), False)
        i = 0
        while i < self.__ntargets:
            x = int(np.random.rand()*self.__w)
            y = int(np.random.rand()*self.__h)
            if self.__targets_mask[x, y] == False and self.__map[x, y] == 0:
                self.__targets_mask[x, y] = True
            else:
                #We have to retry because we extracted the same target before
                continue
            i+=1
        self.__map[self.__targets_mask] = TARGET

    def render(self):
        if self.__rendering:
            self.__screen.fill(BG)
            for x in range(self.__w):
                for y in range(self.__h):
                    if self.__map[x, y] == WALL:
                        rect = pygame.Rect(self.__dw*x, self.__dh*y, self.__dw, self.__dh)
                        pygame.draw.rect(self.__screen, WALL_COLOR, rect)

                    if self.__map[x, y] == TARGET:
                        rect = pygame.Rect(self.__dw*x, self.__dh*y, self.__dw, self.__dh)
                        pygame.draw.rect(self.__screen, TARGET_COLOR, rect)



            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return True

            pygame.display.update()

a = Simulator((100, 100), batch_size=1, agent_size=1, ntargets=3, nwalls=4, rendering=True)

exit = False
while not exit:
    exit = a.render()
