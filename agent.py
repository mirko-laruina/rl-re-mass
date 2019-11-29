import numpy as np

class Agent:
    def __init__(self, initial_x, initial_y, size):
        self.__x = initial_x
        self.__y = initial_y
        self.__size = size