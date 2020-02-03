from simulator import Simulator
import time
import cProfile
from ray.tune.registry import register_env
from ray.rllib.agents import ppo
from ray.rllib.agents.ppo import PPOTrainer
from ray import tune
import ray

ray.init(num_cpus=8)
register_env("drones_env", lambda c: Simulator((100, 100), batch_size=4,
                                        agent_size=2, ntargets=3,
                                        nwalls=4, observation_range=3,
                                        stig_evaporation_speed=0.5, max_steps=1000,
                                    rendering=False))
#trainer = ppo.PPOAgent(env="drones_env")
#while True:
#    print(trainer.train())
tune.run(PPOTrainer, config={"env": "drones_env"})


import sys
sys.exit(0)
a = Simulator((100, 100), batch_size=4,
                agent_size=2, ntargets=3,
                nwalls=4, observation_range=3,
                stig_evaporation_speed=0.5, max_steps=1000,
            rendering=True)
exit = False
f = 0
initial = time.time()
while not exit:
    exit = a.render()
    a.move()
    f+=1
    #print(f/(time.time()-initial))
    print(a.observe())
    if f > 100000:
        exit = True
