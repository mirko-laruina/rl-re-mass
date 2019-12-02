from simulator import Simulator

a = Simulator((100, 100), batch_size=4, agent_size=2, ntargets=3, nwalls=4, rendering=True)

exit = False
while not exit:
    exit = a.render()
    a.move()
