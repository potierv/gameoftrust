import itertools
import logging
import numpy as np
from node import Node, EBelief


def generate_map(size):
    map = np.array(np.arange(0, size * size)).reshape(size, size)
    map = [[Node(str(map[i][j])) for j in range(size)] for i in range(size)]
    logging.info(f'Generated map of size {size}, '
                 f'containing {size * size} nodes.')
    return map


def link_map_nodes(map):
    size = len(map)
    for i in range(size):
        for j in range(size):
            map[i][j].add_links(
                map[i][(j + 1) % size],
                map[i][(j - 1) % size],
                map[(i + 1) % size][j],
                map[(i - 1) % size][j],
            )
    logging.info(f"Linked nodes together.")



def nodes_from_map(map):
    return [x for x in itertools.chain(*map)]


def log_state(map):
    nodes = nodes_from_map(map)
    for n in nodes:
        logging.debug(n.pretty())


def log_map(map, round_number=None):
    if round_number:
        log = f'Round {round_number}\n'
    else:
        log = '\n'
    size = len(map)
    for i in range(size):
        for j in range(size):
            belief = map[i][j].state.belief
            if belief == EBelief.NEUTRAL:
                log += '-'
            elif belief == EBelief.TRUE:
                log += 'X'
            else:
                log += '0'
        if i < size - 1:
            log += '\n'
    logging.info(log)
