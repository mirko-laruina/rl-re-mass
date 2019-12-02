import numpy as np
from agent import Agent
import utils

class World:
    def __init__(self, space_shape, batch_size, agent_size, ntargets, nwalls):
        self.__batch_size = batch_size
        self.__agent_size = agent_size
        self.__agents = []
        self.__ntargets = ntargets
        self.__nwalls = nwalls
        #Max/min wall length is a percentage of space height
        self.__max_wall_len = 0.7
        self.__min_wall_len = 0.3

        self.__w = space_shape[1]
        self.__h = space_shape[0]

        self.map = np.zeros((self.__w, self.__h))

        self.__generate_walls()
        self.__generate_targets()

        self.__initiate_agents()

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
            if self.map[x, 0] == utils.WALL or self.map[x, -1] == utils.WALL:
                continue

            wall_lenght = self.__get_rand_y()*(self.__max_wall_len-self.__min_wall_len)
            wall_lenght += self.__min_wall_len*self.__h
            wall_lenght = int(wall_lenght)
            wall_arr = np.full(self.__h, False)
            wall_arr[:wall_lenght] = True
            reverse = np.random.rand() < 0.5
            self.map[x, wall_arr if not reverse else ~wall_arr] = utils.WALL

            #Check if a path is possible
            #Doesn't work properly
            sum_ = self.map[x, wall_arr]
            if x != 0:
                sum_ += self.map[x-1, wall_arr]
            if x != self.__w-1:
                sum_ += self.map[x+1, wall_arr]
                
            sum_ = np.max(sum_)
            if sum_ > utils.WALL:
                self.map[x, wall_arr if not reverse else ~wall_arr] = 0
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
            if self.__targets_mask[x, y] == False and self.map[x, y] == 0:
                self.__targets_mask[x, y] = True
            else:
                #We have to retry because we extracted the same target before
                continue
            i+=1
        self.map[self.__targets_mask] = utils.TARGET

    def __checkmap_boundaries(self, x1, y1, x2, y2):
        """
        Checks if a block [x1:x2][y1:y2] is inside the map
        """
        if x1 >= 0 and x2 < self.__w:
            if y2 >= 0 and y2 < self.__h:
                return True
        return False

    def __checkmap_free(self, x1, y1, x2, y2):
        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                if self.map[i, j] != 0:
                    return False
        return True

    def check_agent_move(self, x, y, agent_size = 1):
        """
        Check if agent can move in the position described by parameters
        """
        if not self.__checkmap_boundaries(x, y, x+agent_size-1, y+agent_size-1):
            return False
        
        if not self.__checkmap_free(x, y, x+agent_size-1, y+agent_size-1):
            return False
        
        return True

    def __initiate_agents(self):
        """
        Initialization of all the agents
        """
        i = 0
        while i < self.__batch_size:
            x = self.__get_rand_x()
            y = self.__get_rand_y()
            #Check if the random position is not on the border or on walls
            if not self.check_agent_move(x, y, self.__agent_size):
                continue

            self.__agents.append(Agent(self, x, y, self.__agent_size))

            i+=1

    def get_agents(self):
        return self.__agents

    def move(self):
        for i in range(len(self.__agents)):
            self.__agents[i].move()