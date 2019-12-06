from simulator import Simulator
import time
import cProfile

a = Simulator((100, 100), batch_size=4,
                agent_size=2, ntargets=3,
                nwalls=4, observation_range=3,
                stig_evaporation_speed=0.5, max_steps=1000,
            rendering=False)
exit = False
f = 0
initial = time.time()
while not exit:
    exit = a.render()
    a.move()
    f+=1
    print(f/(time.time()-initial))
    if f > 100000:
        exit = True
