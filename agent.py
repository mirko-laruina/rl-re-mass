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
    
    def observe(self):
        base_x = self.__x-self.__obs_range
        base_y = self.__y-self.__obs_range
        size = self.__size+self.__obs_range*2
        obs_matrix = self.__world.observe_map(base_x, base_y, size)
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

    def move(self, dx = 0, dy = 0, random = False):
        if random:
            new_x = self.__x + int(np.random.rand()*3-1.5)
            new_y = self.__y + int(np.random.rand()*3-1.5)
        else:
            new_x = self.__x + dx
            new_y = self.__y + dy
        
        if(self.__world.check_agent_move(new_x, new_y, self.__size)):
            self.__x = new_x
            self.__y = new_y
            self.release_pheromone()
            return True
        else:
            return False
    


    def step(self, action):
        #Action is the direction (for now, at least)
        good = False
        if action[0]:
            good = self.move(-1, 0)
        elif action[1]:
            good = self.move(0, 1)
        elif action[2]:
            good = self.move(1, 0)
        else:
            good = self.move(0, -1)
    
        reward = 0
        if good == True: reward = 1   
        return reward, not good
