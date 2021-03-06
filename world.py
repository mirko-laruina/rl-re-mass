import numpy as np
from agent import Agent
from stigmergic_layer import StigmergicLayer
import utils

class World:
    def __init__(self, space_shape,
                batch_size, agent_size,
                ntargets, nwalls,
                observation_range,
                stig_evaporation_speed):
        """
        space_shape: shape of the explorable space
        batch_size: number of agents
        agent_size: width of an agent (which is assumed as a square)
        ntargets: number of targets randomly generated
        nwalls: number of walls randomly generated
        observation_range: space observable by a single agent,
                            calculated from its side (approximated along the diagonal)
        stig_evaporation_speed: speed at which stigmergy evaporates
        
        """
        self.__batch_size = batch_size
        self.__agent_size = agent_size
        self.__agent_obs_range = observation_range
        self.__agents = {}
        self.__ntargets = ntargets
        self.__nwalls = nwalls
        self.__stig_evaporation_speed = stig_evaporation_speed
        #Max/min wall length is a percentage of space height
        self.__max_wall_len = 0.7
        self.__min_wall_len = 0.3

        self.__w = space_shape[1]
        self.__h = space_shape[0]

        self.nstigs = 3
        self.__extendend_map = np.zeros((self.__w+2*observation_range,
                                        self.__h+2*observation_range, self.nstigs))
        self.__extendend_map[:,:observation_range, utils.NO_MAP] = 1
        self.__extendend_map[-observation_range:,:, utils.NO_MAP] = 1
        self.__extendend_map[:,-observation_range:, utils.NO_MAP] = 1
        self.__extendend_map[:observation_range, :, utils.NO_MAP] = 1

        #Notice: this creates just a reference to a subspace, doesn't allocate new memory
        self.map = self.__extendend_map[observation_range:-observation_range,
                                        observation_range:-observation_range]

        self.stig_layers = []
        stig_bound = StigmergicLayer(self.__extendend_map, utils.NO_MAP,
                                    utils.PHERO_RELEASE_VALUE, self.__stig_evaporation_speed,
                                    utils.OVERLAY_STIG_BOUNDARY)
        stig_wall = StigmergicLayer(self.__extendend_map, utils.WALL,
                                    utils.PHERO_RELEASE_VALUE, self.__stig_evaporation_speed,
                                    utils.OVERLAY_STIG_WALL)
        stig_target = StigmergicLayer(self.__extendend_map, utils.TARGET,
                                    utils.PHERO_RELEASE_VALUE, self.__stig_evaporation_speed,
                                    utils.OVERLAY_STIG_TARGET)                                    
        self.stig_layers.append(stig_bound)
        self.stig_layers.append(stig_wall)
        self.stig_layers.append(stig_target)


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
            if self.map[x, 0, utils.WALL] or self.map[x, -1, utils.WALL]:
                continue

            wall_lenght = self.__get_rand_y()*(self.__max_wall_len-self.__min_wall_len)
            wall_lenght += self.__min_wall_len*self.__h
            wall_lenght = int(wall_lenght)
            wall_arr = np.full(self.__h, False)
            wall_arr[:wall_lenght] = True
            reverse = np.random.rand() < 0.5
            self.map[x, wall_arr if not reverse else ~wall_arr, utils.WALL] = 1

            #Check if a path is possible
            #Doesn't work properly
            sum_ = self.map[x, wall_arr, utils.WALL]
            if x != 0:
                sum_ += self.map[x-1, wall_arr, utils.WALL]
            if x != self.__w-1:
                sum_ += self.map[x+1, wall_arr, utils.WALL]
                
            sum_ = np.max(sum_)
            if sum_ > utils.WALL:
                self.map[x, wall_arr if not reverse else ~wall_arr, utils.WALL] = 0
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
            if self.__targets_mask[x, y] == False and np.sum(self.map[x, y]) == 0:
                self.__targets_mask[x, y] = True
            else:
                #We have to retry because we extracted the same target before
                continue
            i+=1
        self.map[self.__targets_mask, utils.TARGET] = 1

    def __checkmap_boundaries(self, x1, y1, x2, y2):
        """
        Checks if a block [x1:x2][y1:y2] is inside the map
        """
        if x1 >= 0 and x2 < self.__w:
            if y1 >= 0 and y2 < self.__h:
                return True
        return False

    def __checkmap_free(self, x1, y1, x2, y2):
        return not np.any(self.map[x1:x2+1, y1:y2+1])
        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                if np.sum(self.map[i, j]) > 0:
                    return False
        return True

    def observe_map(self, x, y, size):
        #We are in the extended map space, so all points have to be remapped
        min_x = x+self.__agent_obs_range
        min_y = y+self.__agent_obs_range
        max_x = x+size+self.__agent_obs_range
        max_y = y+size+self.__agent_obs_range
        obs_matrix = self.__extendend_map[min_x:max_x, min_y:max_y]
        obs_matrix = np.transpose(obs_matrix)
        for layer in self.stig_layers:
            obs_matrix = np.append(obs_matrix, layer.layer[min_x:max_x, min_y:max_y])

        return obs_matrix.reshape(6, 64)

    def observe(self):
        #Returns dict of all agents observations
        obss = {}
        for agent in self.__agents:
            obss[agent] = self.__agents[agent].observe()

        return obss

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

            self.__agents['agent_'+str(i)] = Agent(self, x, y, self.__agent_size, self.__agent_obs_range)
            i+=1
    
        return self.observe()

    def get_agents(self):
        return self.__agents

    def reset(self):
        self.map.fill(0)
        for layer in self.stig_layers:
            layer.reset()
        self.__generate_walls()
        self.__generate_targets()
        return self.__initiate_agents()

    def step(self, actions):
        #Actions should be a dict where key is the agent
        #and value is the action he should take

        rewards = {}
        dones = {}
        for agent_name, action in actions.items():
            reward, done = self.__agents[agent_name].step(action)
            rewards[agent_name] = reward
            dones[agent_name] = done
        
        new_obss = self.observe()
        dones['__all__'] = any(dones.values())
        return new_obss, rewards, dones, {}


    def move(self):        
        for agent in self.__agents.values():
            agent.move(random=True)

        self.stig_evaporation()

    def stig_evaporation(self):
        for layer in self.stig_layers:
            layer.evaporate()
