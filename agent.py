import numpy as np

class Agent:
    def __init__(self, world, initial_x, initial_y, size, obs_range):
        self.__x = initial_x
        self.__y = initial_y
        self.__world = world
        self.__size = size
        self.__obs_range = obs_range

    def get_pos(self):
        return self.__x, self.__y
    
    def get_size(self):
        return self.__size

    def get_obs_range(self):
        return self.__obs_range

    def move(self):
        #Temporary
        new_x = self.__x + (1 if np.random.rand() < 0.5 else -1)
        new_y = self.__y + (1 if np.random.rand() < 0.5 else -1)
        if(self.__world.check_agent_move(new_x, new_y, self.__size)):
            self.__x = new_x
            self.__y = new_y
