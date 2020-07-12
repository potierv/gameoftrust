import random
import itertools
import logging
import math
import numpy as np
from node import Node, EBelief


class Map:

    def __init__(self, height, width):
        self.height = height
        self.width = width

    def generate(self):
        array = np.array(np.arange(0, self.height * self.width))
        self.map = array.reshape(self.height, self.width)
        self.map = [[Node(str(self.map[i][j])) for j in range(self.width)]
                     for i in range(self.height)]
        logging.info(f'Generated map of height {self.height} '
                     f'and width {self.width}, '
                     f'containing {self.height * self.width} nodes.')


    def link_nodes(self):
        for i in range(self.height):
            for j in range(self.width):
                self.map[i][j].add_links(
                    self.map[i][(j + 1) % self.width],
                    self.map[i][(j - 1) % self.width],
                    self.map[(i + 1) % self.height][j],
                    self.map[(i - 1) % self.height][j],
                    self.map[(i + 1) % self.height][(j + 1) % self.width],
                    self.map[(i + 1) % self.height][(j - 1) % self.width],
                    self.map[(i - 1) % self.height][(j + 1) % self.width],
                    self.map[(i - 1) % self.height][(j - 1) % self.width],
                )
        logging.info(f"Linked nodes together.")


    def add_belief(self, belief, density=0.01, prob=0.9):
        to_add = int(math.ceil(density * self.height * self.width))
        for i in range(to_add):
            x = random.randrange(0, self.width)
            y = random.randrange(0, self.height)
            self.map[y][x].set_belief(belief, prob)


    def get_nodes(self):
        return [x for x in itertools.chain(*self.map)]


    def log_state(self):
        nodes = self.get_nodes()
        for n in nodes:
            logging.debug(n.pretty())


    def log_map(self, round_number=None):
        log = '\n'
        if round_number:
            log = f'Round {round_number}' + log
        for i in range(self.height):
            for j in range(self.width):
                belief = self.map[i][j].state.belief
                if belief == EBelief.NEUTRAL:
                    log += '-'
                elif belief == EBelief.TRUE:
                    log += 'X'
                else:
                    log += '0'
            if i < self.height - 1:
                log += '\n'
        logging.info(log)
