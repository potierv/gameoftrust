#!/usr/bin/env python3
import random
import logging
import itertools
import copy
from node import EBelief, node_changed_state, get_node_by_name
from map import (generate_map, link_map_nodes, nodes_from_map, log_state,
                 log_map)


def random_percentage():
    return (random.randrange(1, 101) / 100.0)


def calc_treshold(node, neighbour):
    return (node.state.prob * (1.0 - neighbour.state.prob))


def convince_neighbours(node, next_nodes):
    convinced_count = 0
    for neighbour in node.neighbours:
        neighbour = get_node_by_name(next_nodes, neighbour)
        if neighbour.state.belief != node.state.belief:
            rand = random_percentage()
            treshold = calc_treshold(node, neighbour)
            if rand < treshold:
                next_neighbour = get_node_by_name(next_nodes, neighbour.name)
                next_neighbour.set_belief(node.state.belief, node.state.prob)
                convinced_count += 1
    return convinced_count


def main():
    size = 20
    map = generate_map(size)
    link_map_nodes(map)

    prev = copy.deepcopy(map)
    map[0][0].set_belief(EBelief.FALSE, 0.5)
    log_state(map)
    log_map(map)

    round_count = 0
    round_convinced = 1
    total_convinced = 0
    while round_convinced:
        next = copy.deepcopy(map)
        prev_nodes = nodes_from_map(prev)
        nodes = nodes_from_map(map)
        next_nodes = nodes_from_map(next)

        round_convinced = 0
        for node in nodes:
            node_convinced = 0
            if node_changed_state(node, prev_nodes):
                node_convinced = convince_neighbours(node, next_nodes)
            round_convinced += node_convinced

        prev = copy.deepcopy(map)
        map = copy.deepcopy(next)
        total_convinced += round_convinced
        round_count += 1
        log_state(map)
        log_map(map, round_count)

    logging.info(f'Stabilisation took {round_count} round(s), '
                 f'{total_convinced} node(s) changed belief.')


if __name__ == '__main__':
    logging.basicConfig(filename='got.log', level=logging.INFO)
    main()
