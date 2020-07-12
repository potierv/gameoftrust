from dataclasses import dataclass
import itertools
import logging
import math
from node import Node, EBelief
import random


@dataclass
class Map:
    width: int
    height: int
    map: list = None

    def generate(self):
        """Generate the map attribute"""
        self.map = [[Node(str(i * self.width + j)) for j in range(self.width)]
                    for i in range(self.height)]
        logging.info(f'Generated map of height {self.height} '
                     f'and width {self.width}, '
                     f'containing {self.height * self.width} nodes.')

    def link_nodes(self):
        """Link each node to every node around it"""
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

    def introduce_belief(self, belief, density=0.01, probability=0.9):
        """Introduce a belief into the map
        :param belief: Belief type
        :type belief: EBelief
        :param density: Density of elements to introduce into the map
        :type density: float
        :param probability: Probability to transmit the belief
        :type probability: float
        """
        for i in range(math.ceil(density * self.height * self.width)):
            x = random.randrange(0, self.width)
            y = random.randrange(0, self.height)
            # TODO We should probably first check that the element doesn't already
            #  trust that belief. If so, we look for another one
            self.map[y][x].set_belief(belief, probability)

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
