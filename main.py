#!/usr/bin/env python3
import os
import logging
import copy
import yaml
from yaml import Loader
from munch import munchify
from node import Belief, node_changed_belief
from map import Map


def load_config(config_dir='config', default='default.yml', user='user.yml'):
    # Default configuration
    config_dir = os.path.join('.', config_dir)
    with open(os.path.join(config_dir, default), 'r') as f:
        config = yaml.load(f, Loader=Loader)
    munch = munchify(config)
    # User provided configuration
    user_filename = os.path.join(config_dir, user)
    if os.path.exists(user_filename):
        with open(user_filename, 'r') as f:
            user_config = yaml.load(f, Loader=Loader)
        config.update(user_config)
    munch = munchify(config)
    munch.map.height = munch.map.get('height', munch.map.width)
    return munch


def main():
    config = load_config()
    game_map = Map(width=config.map.width, height=config.map.height)
    game_map.generate()
    game_map.link_nodes()

    prev = copy.deepcopy(game_map)

    positive_set = game_map.introduce_belief(Belief.TRUE,
                                             density=config.positive.density,
                                             confidence=config.positive.confidence)
    negative_set = game_map.introduce_belief(Belief.FALSE,
                                             density=config.negative.density,
                                             confidence=config.negative.confidence)
    round_count = 0
    game_map.log_state()
    game_map.log_map(round_count, config.gui)

    total_convinced = 0
    prev_round_convinced = set(positive_set).union(negative_set)
    while prev_round_convinced:
        game_map_copy = copy.deepcopy(game_map)
        nodes = game_map.get_nodes()
        next_nodes = game_map_copy.get_nodes()

        round_convinced = set()
        for name in prev_round_convinced:
            node = nodes[name]
            convinced_nodes = node.convince_neighbours(nodes=next_nodes)
            round_convinced.update(convinced_nodes)

        round_count += 1
        total_convinced += len(round_convinced)
        prev_round_convinced = round_convinced
        game_map = game_map_copy
        game_map.log_state()
        game_map.log_map(round_count, config.gui)

    logging.info(f"Stabilisation took {round_count} round(s), "
                 f"{total_convinced} node(s) changed belief.")


if __name__ == '__main__':
    logging.basicConfig(filename='got.log', level=logging.INFO)
    main()
