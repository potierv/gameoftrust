import random
import logging
import copy
from node import Belief, node_changed_belief, get_node_by_name
from map import Map


def random_percentage():
    return random.randrange(1, 101) / 100


def calc_treshold(node, neighbour):
    return node.state.probability * (1.0 - neighbour.state.probability)


def convince_neighbours(node, next_nodes):
    convinced_count = 0
    for neighbour in node.neighbours:
        neighbour = get_node_by_name(next_nodes, neighbour)
        if neighbour.state.belief != node.state.belief:
            rand = random_percentage()
            treshold = calc_treshold(node, neighbour)
            if rand < treshold:
                next_neighbour = get_node_by_name(next_nodes, neighbour.name)
                next_neighbour.set_belief(node.state.belief, node.state.probability)
                convinced_count += 1
    return convinced_count


def main():
    width = 50
    height = 20
    game_map = Map(width=width, height=height)
    game_map.generate()
    game_map.link_nodes()

    prev = copy.deepcopy(game_map)

    game_map.introduce_belief(Belief.TRUE, density=0.02, probability=0.5)
    game_map.introduce_belief(Belief.FALSE, density=0.1, probability=0.25)

    game_map.log_state()
    game_map.log_map()

    round_count = 0
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
            if node_changed_belief(node, prev_nodes):
                node_convinced = convince_neighbours(node, next_nodes)
            round_convinced += node_convinced

        prev = copy.deepcopy(game_map)
        game_map = copy.deepcopy(game_map_copy)
        total_convinced += round_convinced
        round_count += 1
        game_map.log_state()
        game_map.log_map(round_count)

    logging.info(f"Stabilisation took {round_count} round(s), "
                 f"{total_convinced} node(s) changed belief.")


if __name__ == '__main__':
    logging.basicConfig(filename='got.log', level=logging.INFO)
    main()
