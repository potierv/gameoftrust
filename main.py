#!/usr/bin/env python3
import logging
import copy
from node import Belief, node_changed_belief
from map import Map


def main():
    width = 50
    height = 20
    gui = False
    game_map = Map(width=width, height=height)
    game_map.generate()
    game_map.link_nodes()

    prev = copy.deepcopy(game_map)

    game_map.introduce_belief(Belief.TRUE, density=0.02, confidence=0.5)
    game_map.introduce_belief(Belief.FALSE, density=0.1, confidence=0.25)

    round_count = 0
    game_map.log_state()
    game_map.log_map(round_count, gui)

    round_convinced = 1
    total_convinced = 0
    while round_convinced:
        game_map_copy = copy.deepcopy(game_map)
        prev_nodes = prev.get_nodes()
        nodes = game_map.get_nodes()
        next_nodes = game_map_copy.get_nodes()

        round_convinced = 0
        for node in nodes:
            node_convinced = 0
            if node_changed_belief(node=node, prev_nodes=prev_nodes):
                node_convinced = node.convince_neighbours(nodes=next_nodes)
            round_convinced += node_convinced

        prev = copy.deepcopy(game_map)
        game_map = copy.deepcopy(game_map_copy)
        total_convinced += round_convinced
        round_count += 1
        game_map.log_state()
        game_map.log_map(round_count, gui)

    logging.info(f"Stabilisation took {round_count} round(s), "
                 f"{total_convinced} node(s) changed belief.")


if __name__ == '__main__':
    logging.basicConfig(filename='got.log', level=logging.INFO)
    main()
