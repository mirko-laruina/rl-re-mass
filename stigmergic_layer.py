import numpy as np

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
    
    def verify(self, map_value):
        """
        True if the map cell triggers pheromone release
        Using a function allows more customization
        """
        if map_value == self.__cond:
            return True
        return False

    """ Too expensive
    def iter_release(self, x, y, value):
        if value < 1:
            return
        
        try:
            self.__layer[x, y] += value
            if self.__layer[x, y] > 255: 
                self.__layer[x, y] = self.__phero_value 
        except:
            return

        for i in range(x-1,x+2):
            for j in range(y-1,y+2):
                if i == x and j == y:
                    continue
                self.iter_release(i, j, value/4)
    """

    def update_level(self, x, y, new_level):
        if self.__layer[x, y] < new_level:
            self.__layer[x, y] = new_level

    def conditional_release(self, map_value, x, y):
        """
        Releases the pheromone (and returns true) if the conditions are met
        """
        if(self.verify(map_value)):
            #self.__layer[x-1:x+1, y-1:y+1] = self.__phero_value
            #Draw a circle around the release_point
            radius = self.__phero_value//self.__decay + 1
            for dy in range(radius):
                #start from the top of the circle and go down
                #x**2 + y**2 = r**2
                #x = sqrt(r**2 - y**2) = r*sqrt(1-y**2/r**2) ~= r*(1 + 0.5*(-y**2/r**2)) (taylor O(x**2))
                max_dx = int(radius*(1 - 0.5*(dy**2)/(radius**2)))
                
                for dx in range(0, max_dx+1):
                    phero_level = (1-(dx**2 + dy**2)/(radius**2))*self.__phero_value
                    if x - dx > 0:
                        if y - dy > 0:
                            self.update_level(x-dx, y-dy, phero_level)
                        if y + dy < self.__layer.shape[1]:   
                            self.update_level(x-dx, y+dy, phero_level)
                    
                    if x + dx < self.__layer.shape[0]:
                        if y - dy > 0:
                            self.update_level(x+dx, y-dy, phero_level)
                        if y + dy < self.__layer.shape[1]:                       
                            self.update_level(x+dx, y+dy, phero_level)



            #if self.__lay
            return True
        return False

    def evaporate(self):
        self.__layer -= self.__evap_speed
        self.__layer[self.__layer < 0] = 0

    def value(self, x, y):
        return self.__layer[x, y]
