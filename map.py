from dataclasses import dataclass
import itertools
import logging
import math
import json
import random
from node import Node, Belief


@dataclass
class Map:
    width: int
    height: int
    map: list = None
    nodes: dict = None

    def generate(self):
        """Generate the map attribute"""
        self.map = [[Node(str(i * self.width + j)) for j in range(self.width)]
                    for i in range(self.height)]
        self.nodes = dict([(node.name, node)
                           for node in itertools.chain(*self.map)])
        logging.info(f"Generated map of height {self.height} "
                     f"and width {self.width}, "
                     f"containing {self.height * self.width} nodes.")

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

    def introduce_belief(self, belief: Belief, density: float = 0.01,
                         confidence: float = 0.9):
        """Introduce a belief into the map
        :param belief: Belief type
        :type belief: Belief
        :param density: Density of elements to introduce into the map
        :type density: float
        :param confidence: Confidence in the belief
        :type confidence: float
        """
        changed = set()
        nodes = [node.name for node in self.nodes.values()
                 if node.state.belief == Belief.NEUTRAL]
        for i in range(math.ceil(density * self.height * self.width)):
            if len(nodes) == 0:
                logging.warn(f"Could not satisfy desired density")
                break
            random_index = random.randrange(0, len(nodes))
            random_name = nodes[random_index]
            self.nodes[random_name].set_belief(belief=belief,
                                               confidence=confidence)
            del nodes[random_index]
            changed.add(random_name)
        achieved_density = len(changed) / (self.width * self. height)
        logging.info(f"Introduced {len(changed)} {str(belief)} beliefs. "
                     f"Achieved density: {achieved_density}.")
        return changed

    def get_nodes(self):
        """Return map nodes"""
        return self.nodes

    def log_state(self):
        """Log map state"""
        # Is that only used for a debug purpose ?
        for name, node in self.get_nodes().items():
            logging.debug(node.get_pretty_display())

    def as_json(self, round_number: int = None):
        """Converts the Map object to a json to feed the GUI."""
        out = json.dumps({
            "round": round_number,
            "map": self.map,
        }, default=lambda o: str(o.state.belief))
        return out

    def log_map(self, round_number: int = None, gui: bool = False):
        """Log a representation of the map
        :param round_number: Round number
        :type round_number: int
        """
        if round_number:
            log = f"Round {round_number}\n"
        else:
            log = "\n"

        # TODO We might be able to do that in a better way, idk
        map_display_lines = ["".join([str(self.map[i][j].state.belief)
                             for j in range(self.width)])
                             for i in range(self.height)]

        log += '\n'.join(map_display_lines)

        logging.info(log)
        if gui:
            print(self.as_json(round_number))
