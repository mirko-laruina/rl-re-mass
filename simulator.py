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
    def __init__(self, space_shape, ntargets, nwalls):
        self.render_space_shape = (1000, 1000)
        self.ntargets = ntargets
        self.nwalls = nwalls
        #Max/min wall length is a percentage of space height
        self.max_wall_len = 0.7
        self.min_wall_len = 0.3
        self.w = space_shape[0]
        self.h = space_shape[1]

        #How much is the step in the render space
        self.dw = self.render_space_shape[0]/self.w
        self.dh = self.render_space_shape[1]/self.h

        self.screen = pygame.display.set_mode(self.render_space_shape)
        #self.map_bitmap = map_bitmap
        #self.map = np.asarray(Image.open('example-map.bmp'))
        #self.map = np.unpackbits(self.map, axis=2)
        self.map = np.zeros((self.w, self.h))

        self.generateWalls()
        self.generateTargets()

    def generateWalls(self):
        #We generate nwalls based on the x, with a random lenght
        #This has to be done BEFORE picking the targets
        #That's not the best method and it is NOT guarenteed to work
        #Can cycle forever
        #Ex. with high number of walls
        # THIS HAS TO BE EDITED
        i = 0
        while i < self.nwalls:
            x = int(np.random.rand()*self.w)
            if self.map[x, 0] == WALL or self.map[x, -1] == WALL:
                continue

            wall_lenght = np.random.rand()*self.h*(self.max_wall_len-self.min_wall_len)
            wall_lenght += self.min_wall_len*self.h
            wall_lenght = int(wall_lenght)
            wall_arr = np.full(self.h, False)
            wall_arr[:wall_lenght] = True
            reverse = np.random.rand() < 0.5
            self.map[x, wall_arr if not reverse else ~wall_arr] = WALL

            #Check if a path is possible
            #Doesn't work properly
            sum = self.map[x, wall_arr]
            if x != 0:
                sum += self.map[x-1, wall_arr]
            if x != self.w-1:
                sum += self.map[x+1, wall_arr]
                
            sum = np.max(sum)
            if sum > WALL:
                self.map[x, wall_arr if not reverse else ~wall_arr] = 0
                continue 

            i+=1

    def generateTargets(self):
        #We pick ntargets points in the space
        self.targets_mask = np.full((self.w, self.h), False)
        i = 0
        while i < self.ntargets:
            x = int(np.random.rand()*self.w)
            y = int(np.random.rand()*self.h)
            if self.targets_mask[x, y] == False and self.map[x, y] == 0:
                self.targets_mask[x, y] = True
            else:
                #We have to retry because we extracted the same target before
                continue
            i+=1
        self.map[self.targets_mask] = TARGET

    def render(self):
        #render_map = np.array
        self.screen.fill(BG)
        for x in range(self.w):
            for y in range(self.h):
                if self.map[x, y] == WALL:
                    rect = pygame.Rect(self.dw*x, self.dh*y, self.dw, self.dh)
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)

                if self.map[x, y] == TARGET:
                    rect = pygame.Rect(self.dw*x, self.dh*y, self.dw, self.dh)
                    pygame.draw.rect(self.screen, TARGET_COLOR, rect)



        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True

        pygame.display.update()

a = Simulator((100, 100), 20, 4)

exit = False
while not exit:
    exit = a.render()
