from dataclasses import dataclass
from enum import Enum, auto
import logging
from utils import random_percentage


class Belief(Enum):
    NEUTRAL = auto()
    TRUE = auto()
    FALSE = auto()

    def __str__(self):
        return {
            self.NEUTRAL: '-',
            self.TRUE: 'X',
            self.FALSE: '0',
        }[self]


@dataclass
class NodeState:
    belief: Belief
    confidence: float

    def __repr__(self):
        return f'{self.belief}: {self.confidence}'


class Node:

    def __init__(self, name, state=Belief.NEUTRAL, confidence=0.01):
        self.name = name
        self.state = NodeState(state, confidence)
        self.neighbours = set()
        logging.debug(f"Created node {name}.")
        logging.debug(f"{self.get_pretty_display()}.")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def get_pretty_display(self):
        if self.neighbours:
            neighbours = ", ".join([str(n) for n in self.neighbours])
        else:
            neighbours = "None"
        return f"{self.name}: {self.state}. Links: {neighbours}"

    def add_link(self, node):
        """Link current entity with node
        :param node: Node to link
        :type node: Node
        """
        if node is self:
            logging.debug(f'Trying to link {self} to itself.')
        else:
            if node.name not in self.neighbours:
                self.neighbours.add(node.name)
                logging.debug(f"Linked {node} as {self}'s neighbour.")
            else:
                logging.debug(f"{node} is already a neighbour of {self}.")
            if self.name not in node.neighbours:
                node.neighbours.add(self.name)
                logging.debug(f"Created reciprocal link of {self} to {node}.")
            else:
                logging.debug(f"{self} is already a neighbour of {node}.")

    def set_belief(self, belief, confidence):
        """Set belief
        :param belief: Belief type
        :type belief: Belief
        :param confidence: confidence in the belief
        :type confidence: float
        """
        self.state.belief = belief
        self.state.confidence = confidence

    def add_links(self, *nodes):
        """Link current entity with every node"""
        for node in nodes:
            self.add_link(node=node)

    def calculate_treshold(self, neighbour):
        """Calculate the treshold at which we consider
         a neighbour is convinced"""
        return self.state.confidence * (1.0 - neighbour.state.confidence)

    def engage_conversation(self, nodes, neighbour):
        """Trying to convince a neighbour by drawing a random number.
        If that number is superior the a certain treshold, the neighbour is
        convinced. Its belief is changed and its confidence is set to the
        node's confidence."""
        treshold = self.calculate_treshold(neighbour)
        if random_percentage() < treshold:
            next_neighbour = nodes[neighbour.name]
            next_neighbour.set_belief(belief=self.state.belief,
                                      confidence=self.state.confidence)
            return True
        return False

    def convince_neighbours(self, nodes):
        """Engages a conversation with the neighbours whom have different
        belief to the node's one."""
        convinced_neighbours = set()
        for name in self.neighbours:
            neighbour = nodes[name]
            if neighbour.state.belief != self.state.belief:
                if self.engage_conversation(nodes, neighbour) is True:
                    convinced_neighbours.add(neighbour.name)
        return convinced_neighbours


def node_changed_belief(node: Node, prev_nodes: [Node]):
    """Compare node belief and node's previous belief and indicates if they
       are different or not
    :param node: Node
    :type node: Node
    :param prev_nodes: List of previous nodes
    :type prev_nodes: list of Node
    :return: True if the node changed belief compared to the previous,
             False if it's the same
    :rtype: bool
    """
    prev = prev_nodes[node.name]
    return prev.state.belief != node.state.belief
