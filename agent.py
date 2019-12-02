import numpy as np
import utils

class Agent:
    def __init__(self, world, initial_x, initial_y, size, obs_range):
        self.__x = initial_x
        self.__y = initial_y
        self.__world = world
        self.__size = size
        self.__obs_range = obs_range
        self.__obs_shape = (size+2*obs_range, size+2*obs_range)

    def get_pos(self):
        return self.__x, self.__y
    
    def get_size(self):
        return self.__size

    def get_obs_range(self):
        return self.__obs_range

    def release_pheromone(self):
        base_x = self.__x-self.__obs_range
        base_y = self.__y-self.__obs_range
        size = self.__size+self.__obs_range*2
        obs_matrix = self.__world.observe(base_x, base_y, size)
        for i in range(obs_matrix.shape[0]):
            for j in range(obs_matrix.shape[1]):
                if obs_matrix[i, j] == utils.NO_MAP:
                    self.__world.stig_boundary[self.__x, self.__y] = 1
                if obs_matrix[i, j] == utils.WALL:
                    self.__world.stig_wall[self.__x, self.__y] = 1
                if obs_matrix[i, j] == utils.TARGET:
                    self.__world.stig_target[self.__x, self.__y] = 1

    def move(self):
        #Temporary
        new_x = self.__x + (1 if np.random.rand() < 0.5 else -1)
        new_y = self.__y + (1 if np.random.rand() < 0.5 else -1)
        if(self.__world.check_agent_move(new_x, new_y, self.__size)):
            self.__x = new_x
            self.__y = new_y

        self.release_pheromone()