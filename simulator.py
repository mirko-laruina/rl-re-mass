import pygame
import numpy as np
import time

BG = pygame.Color(15, 15, 15) #Black (but not too much)
TARGET_COLOR = pygame.Color(255, 255, 0) #Yellow
WALL_COLOR = pygame.Color(255, 0, 0)
AGENT_COLOR = pygame.Color(15, 50, 255)

TARGET = 1
WALL = 2


class Simulator:
    def __init__(self, space_shape, batch_size, agent_size, ntargets, nwalls, rendering):
        self.__render_space_shape = (1000, 1000)
        self.__batch_size = batch_size
        self.__agent_size = agent_size
        self.__agents = np.array(self.__batch_size)
        self.__ntargets = ntargets
        self.__nwalls = nwalls
        self.__rendering = rendering
        #Max/min wall length is a percentage of space height
        self.__max_wall_len = 0.7
        self.__min_wall_len = 0.3

        self.__w = space_shape[1]
        self.__h = space_shape[0]

        #How much is the step in the render space
        self.__dw = self.__render_space_shape[0]/self.__w
        self.__dh = self.__render_space_shape[1]/self.__h

        self.__map = np.zeros((self.__w, self.__h))
        self.__agent_layer = np.copy(self.__map)

        self.__generate_walls()
        self.__generate_targets()

        self.__initiate_agents()
        self.__screen = pygame.display.set_mode(self.__render_space_shape)

    def __get_rand_x(self):
        return int(np.random.rand()*self.__w)
    
    def __get_rand_y(self):
        return int(np.random.rand()*self.__h)

    def __generate_walls(self):
        """
        We generate nwalls based on the x, with a random lenght
        This has to be done BEFORE picking the targets
        That's not the best method and it is NOT guarenteed to work
        Can cycle forever
        Ex. with high number of walls
        THIS HAS TO BE EDITED
        """
        i = 0
        while i < self.__nwalls:
            x = self.__get_rand_x()
            if self.__map[x, 0] == WALL or self.__map[x, -1] == WALL:
                continue

            wall_lenght = self.__get_rand_y()*(self.__max_wall_len-self.__min_wall_len)
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
        """
        We pick ntargets points in the space as targets
        """
        self.__targets_mask = np.full((self.__w, self.__h), False)
        i = 0
        while i < self.__ntargets:
            x = self.__get_rand_x()
            y = self.__get_rand_y()
            if self.__targets_mask[x, y] == False and self.__map[x, y] == 0:
                self.__targets_mask[x, y] = True
            else:
                #We have to retry because we extracted the same target before
                continue
            i+=1
        self.__map[self.__targets_mask] = TARGET

    def __check_map_boundaries(self, x1, y1, x2, y2):
        """
        Checks if a block [x1:x2][y1:y2] is inside the map
        """
        if x1 >= 0 and x2 < self.__w:
            if y2 >= 0 and y2 < self.__h:
                return True
        return False

    def __check_map_free(self, x1, y1, x2, y2):
        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                if self.__map[i, j] != 0:
                    return False
        return True

    def __check_agent_move(self, x, y, agent_size = 1):
        """
        Check if agent can move in the position described by parameters
        """
        if not self.__check_map_boundaries(x, y, x+agent_size-1, y+agent_size-1):
            return False
        
        if not self.__check_map_free(x, y, x+agent_size-1, y+agent_size-1):
            return False
        
        return True

    def __draw_agent(self, x, y, agent_size = 1):
        for i in range(x, x+agent_size):
            for j in range(y, y+agent_size):
                self.__agent_layer[i, j] = 1

    def __initiate_agents(self):
        """
        Initialization of all the agents
        """
        i = 0
        while i < self.__batch_size:
            x = self.__get_rand_x()
            y = self.__get_rand_y()
            if not self.__check_agent_move(x, y, self.__agent_size):
                continue

            self.__draw_agent(x, y, self.__agent_size)

            i+=1

    def render(self):
        if self.__rendering:
            self.__screen.fill(BG)
            for x in range(self.__w):
                for y in range(self.__h):
                    # Draw walls
                    if self.__map[x, y] == WALL:
                        rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                            int(self.__dw), int(self.__dh))
                        pygame.draw.rect(self.__screen, WALL_COLOR, rect)

                    # Draw targets
                    if self.__map[x, y] == TARGET:
                        rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                            int(self.__dw), int(self.__dh))
                        pygame.draw.rect(self.__screen, TARGET_COLOR, rect)

                    # Draw agents
                    if self.__agent_layer[x, y] == 1:
                        rect = pygame.Rect(int(self.__dw*x), int(self.__dh*y),
                                            int(self.__dw), int(self.__dh))
                        pygame.draw.rect(self.__screen, AGENT_COLOR, rect)


            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return True

            pygame.display.update()

a = Simulator((100, 100), batch_size=4, agent_size=2, ntargets=3, nwalls=4, rendering=True)

exit = False
while not exit:
    exit = a.render()
