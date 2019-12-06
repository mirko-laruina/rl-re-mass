import numpy as np
import math

class StigmergicLayer:
    def __init__(self, map_, release_condition, release_value, evaporation_speed, color = None, decay_speed = 20):
        """
        Defines and manages a stigmergic layer
        
        map_: it is needed to match the dimension of the map in which the stig layer works
        release_condition: which map value should trigger the pheromone release
        release_value: value ("strenght") of the pheromone released
        evaporation_speed: value (num of steps) at which the pheromone effect decreases
        color: if reading the layer is needed for rendering,
               this value can be used
        decay_speed: to be implemented, how far should the pheromone reach
        """
        self.__layer = np.zeros(map_.shape)
        self.__cond = release_condition
        self.__phero_value = release_value
        self.__evap_speed = evaporation_speed
        self.__decay = decay_speed
        self.color = color


        #Caching values for the release
        self.__radius = self.__phero_value//self.__decay + 1
        self.__y_x = []
        
        #x**2 + y**2 = r**2
        #x = sqrt(r**2 - y**2) = r*sqrt(1-y**2/r**2) ~= r*(1 + 0.5*(-y**2/r**2)) (taylor O(x**2))
        for dy in range(self.__radius+1):
            self.__y_x.append(int(math.sqrt(self.__radius**2 - dy**2)))

        self.__partial_phero_map = np.zeros((self.__radius+1, self.__radius+1))
        for dy in range(self.__radius+1):
            #start from the top of the circle and go down
            max_dx = self.__y_x[dy]
            for dx in range(0, max_dx+1):
                self.__partial_phero_map[dx, dy] = (1-(dx**2 + dy**2)/(self.__radius**2))*self.__phero_value

        self.__phero_map = np.zeros((2*self.__radius+2, 2*self.__radius+2))
        #Draw a circle around the release_point
        for dy in range(self.__radius+1):
            for dx in range(0, self.__y_x[dy]):
                phero_level = self.__partial_phero_map[dx, dy]
                x = self.__radius
                y = self.__radius
                self.__phero_map[x-dx, y-dy] = phero_level
                self.__phero_map[x-dx, y+dy] = phero_level
                self.__phero_map[x+dx, y-dy] = phero_level
                self.__phero_map[x+dx, y+dy] = phero_level

    def conditional_release(self, cell_type, x, y):
        """
        Releases the pheromone (and returns true) if the conditions are met
        """
        if(cell_type == self.__cond):
            min_x = x-self.__radius
            max_x = x+self.__radius+1
            min_y = y-self.__radius
            max_y = y+self.__radius+1
            
            
            if min_x < 0:
                min_x = 0
            if max_x >= self.__layer.shape[0]:
                max_x = self.__layer.shape[0]
            if min_y < 0:
                min_y = 0
            if max_y >= self.__layer.shape[1]:
                max_y = self.__layer.shape[1]
            
            new_min_x = min_x-x+self.__radius
            new_max_x = max_x-x+self.__radius
            new_min_y = min_y-y+self.__radius
            new_max_y = max_y-y+self.__radius

            to = self.__layer[min_x:max_x, min_y:max_y]
            from_ = self.__phero_map[new_min_x:new_max_x, new_min_y:new_max_y]
            #Vectorization at its finest
            indexes = to < from_
            to[indexes] = from_[indexes]
            return True
        return False

    def evaporate(self):
        self.__layer -= self.__evap_speed
        self.__layer[self.__layer < 0] = 0

    def value(self, x, y):
        return self.__layer[x, y]
