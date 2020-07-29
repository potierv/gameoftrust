#!/usr/bin/env python3
import os
import logging
import yaml
from yaml import Loader
from munch import munchify
from node import Belief
from map import Map
from roundcontroller import RoundController


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


def initialize_map(config):
    game_map = Map(width=config.map.width, height=config.map.height)
    game_map.generate()
    game_map.link_nodes()
    return game_map


def introduce_beliefs(game_map, config):
    positive_set = game_map.introduce_belief(
        Belief.TRUE,
        density=config.positive.density,
        confidence=config.positive.confidence)
    negative_set = game_map.introduce_belief(
        Belief.FALSE,
        density=config.negative.density,
        confidence=config.negative.confidence)
    return set(positive_set).union(negative_set)


def log_round(game_map, config, round_count):
    game_map.log_state()
    game_map.log_map(round_count, config.gui)


def main():
    config = load_config()
    game_map = initialize_map(config)
    prev_round_convinced = introduce_beliefs(game_map, config)
    nodes = game_map.get_nodes()

    round_count = 0
    total_convinced = 0
    log_round(game_map, config, round_count)
    while prev_round_convinced:
        round_convinced = RoundController(
            nodes,
            prev_round_convinced).get_round_convinced()

        for name in round_convinced:
            nodes.get(name).set_belief(*round_convinced[name])

        round_count += 1
        prev_round_convinced = set(round_convinced.keys())
        total_convinced += len(round_convinced)
        log_round(game_map, config, round_count)

    logging.info(f"Stabilisation took {round_count} round(s), "
                 f"{total_convinced} node(s) changed belief.")


if __name__ == '__main__':
    logging.basicConfig(filename='got.log', level=logging.INFO)
    main()
