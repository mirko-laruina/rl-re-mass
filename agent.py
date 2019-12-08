import numpy as np
import utils

class Agent:
    def __init__(self, world, initial_x, initial_y, size, obs_range):
        self.__x = initial_x
        self.__y = initial_y
        self.__world = world
        self.world = world
        self.__size = size
        self.__obs_range = obs_range
        self.__obs_shape = (size+2*obs_range, size+2*obs_range)

    def get_pos(self):
        return self.__x, self.__y
    
    def get_size(self):
        return self.__size

    def get_obs_range(self):
        return self.__obs_range
    
    def observe(self):
        base_x = self.__x-self.__obs_range
        base_y = self.__y-self.__obs_range
        size = self.__size+self.__obs_range*2
        obs_matrix = self.__world.observe(base_x, base_y, size)
        return obs_matrix

    def release_pheromone(self):
        obs_matrix = self.observe()
        
        # Release should be done at x+size/2, not x (same for y)
        x = self.__x + self.__size//2
        y = self.__y + self.__size//2

        #List of all the elements that trigger pheromone release        
        layers = self.__world.stig_layers
        for layer in layers:
            if np.any(obs_matrix[layer.cond]):
                layer.release(x, y)

    def move(self):
        #Temporary
        new_x = self.__x + (1 if np.random.rand() < 0.5 else -1)
        new_y = self.__y + (1 if np.random.rand() < 0.5 else -1)
        if(self.__world.check_agent_move(new_x, new_y, self.__size)):
            self.__x = new_x
            self.__y = new_y
            self.release_pheromone()
