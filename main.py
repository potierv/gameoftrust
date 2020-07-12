#!/usr/bin/env python3
import logging
import copy
from node import Belief, node_changed_belief
from map import Map

import yaml
from yaml import Loader
from munch import munchify


def load_config(filename='config.yml'):
    with open(filename, 'r') as f:
        config_dict = yaml.load(f, Loader=Loader)
    munch = munchify(config_dict)
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
    prev_round_convinced = set(positive_set).union(*negative_set)
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
