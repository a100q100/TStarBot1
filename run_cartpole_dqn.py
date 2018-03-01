import sys
import torch
import os
import traceback
from absl import app
from absl import flags
import gym

from wrappers.cart_pole_rescale import CartPoleRescaleWrapper
from agents.dqn_agent import DQNAgent

FLAGS = flags.FLAGS
flags.DEFINE_integer("memory_size", 10000, "Experience replay size.")
flags.DEFINE_float("eps_start", 0.9, "Max greedy epsilon for exploration.")
flags.DEFINE_float("eps_end", 0.05, "Min greedy epsilon for exploration.")
flags.DEFINE_integer("eps_decay", 200, "Greedy epsilon decay step.")
flags.DEFINE_float("learning_rate", 1e-2, "Learning rate.")
flags.DEFINE_integer("batch_size", 128, "Batch size.")
flags.DEFINE_float("discount", 0.999, "Discount.")
flags.DEFINE_string("init_model_path", None, "Filepath to load initial model.")
flags.DEFINE_string("save_model_dir", "./checkpoints/", "Dir to save models to")
flags.DEFINE_integer("save_model_freq", 10000, "Model saving frequency.")
flags.FLAGS(sys.argv)

def create_env():
    env = gym.make('CartPole-v0').unwrapped
    env = CartPoleRescaleWrapper(env)
    return env


def train():
    if FLAGS.save_model_dir and not os.path.exists(FLAGS.save_model_dir):
        os.mkdir(FLAGS.save_model_dir)

    env = create_env()
    agent = DQNAgent(
        observation_space=env.observation_space,
        action_space=env.action_space,
        learning_rate=FLAGS.learning_rate,
        batch_size=FLAGS.batch_size,
        discount=FLAGS.discount,
        eps_start=FLAGS.eps_start,
        eps_end=FLAGS.eps_end,
        eps_decay=FLAGS.eps_decay,
        memory_size=FLAGS.memory_size,
        init_model_path=FLAGS.init_model_path,
        save_model_dir=FLAGS.save_model_dir,
        save_model_freq=FLAGS.save_model_freq)

    try:
        agent.learn(env)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    env.close()


def main(argv):
    train()


if __name__ == '__main__':
    app.run(main)
