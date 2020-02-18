from gym.spaces import Discrete, Box, Dict, Tuple
import numpy as np
import ray, gym
from ray import tune
from ray.tune import register_env, grid_search
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.rllib.agents.qmix.qmix_policy import ENV_STATE, QMixTorchPolicy, QMixLoss
from simulator import Simulator

params = {
        "space_shape": (100, 100),
        "batch_size": 4,
        "agent_size": 2,
        "ntargets": 3,
        "nwalls": 4,
        "observation_range": 3,
        "stig_evaporation_speed": 0.5,
        "max_steps": 1000,
        "rendering": False
        }

def env_creator(config):
    env = Simulator(config)

    agents = env.get_agents()
    n_agents = len(agents)
    grouping = {
        "group_1": agents
    }
    obs = Dict({
        "obs": env.observation_space})
    obs_space = Tuple([obs for i in agents])

    act_space = Tuple([env.action_space]*n_agents)
    return env.with_agent_groups(grouping, obs_space=obs_space, act_space=act_space)

register_env("drones", env_creator)

config = {
    "sample_batch_size": 1,
    "train_batch_size": 1,
    "num_workers": 1,
    "num_cpus_per_worker": 3,
    "memory": 0,
    "buffer_size": 100000,
    "mixer": "qmix",
    "env_config": params,
}

ray.init(object_store_memory=2e+9, redis_max_memory=10**9)
tune.run(
    "QMIX",
    stop={
        "timesteps_total": 500000,
        "episode_reward_mean": 5000
    },
    config=dict(config, **{
        "env": "drones",
    }),
    checkpoint_at_end=True
)
