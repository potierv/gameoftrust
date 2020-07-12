#!/usr/bin/env python3
import random
import logging
import copy
from node import EBelief, node_changed_state, get_node_by_name
from map import Map


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
    height = 20
    width = 50
    map = Map(height, width)
    map.generate()
    map.link_nodes()

    prev = copy.deepcopy(map)

    map.add_belief(EBelief.TRUE, density=0.02, prob=0.5)
    map.add_belief(EBelief.FALSE, density=0.1, prob=0.25)

    map.log_state()
    map.log_map()

    round_count = 0
    round_convinced = 1
    total_convinced = 0
    while round_convinced:
        next = copy.deepcopy(map)
        prev_nodes = prev.get_nodes()
        nodes = map.get_nodes()
        next_nodes = next.get_nodes()

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
        map.log_state()
        map.log_map(round_count)

    logging.info(f'Stabilisation took {round_count} round(s), '
                 f'{total_convinced} node(s) changed belief.')


if __name__ == '__main__':
    logging.basicConfig(filename='got.log', level=logging.INFO)
    main()
