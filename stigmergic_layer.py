import numpy as np

class StigmergicLayer:
    def __init__(self, map_, release_condition, release_value, evaporation_speed, color = None, decay_speed = 0):
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
    
    def verify(self, map_value):
        """
        True if the map cell triggers pheromone release
        Using a function allows more customization
        """
        if map_value == self.__cond:
            return True
        return False

    def conditional_release(self, map_value, x, y):
        """
        Releases the pheromone (and returns true) if the conditions are met
        """
        if(self.verify(map_value)):
            self.__layer[x, y] = self.__phero_value
            return True
        return False

    def evaporate(self):
        self.__layer -= self.__evap_speed
        self.__layer[self.__layer < 0] = 0

    def value(self, x, y):
        return self.__layer[x, y]
