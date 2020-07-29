import copy
import logging
import operator
import functools
import random
from dataclasses import dataclass
from enum import Enum, auto
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

    def __init__(self, name, state=Belief.NEUTRAL, confidence=0.9):
        self.name = name
        self.state = NodeState(state, confidence)
        self.previous_state = NodeState(state, confidence)
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
        self.previous_state = copy.copy(self.state)
        self.state.belief = belief
        self.state.confidence = confidence

    def add_links(self, *nodes):
        """Link current entity with every node"""
        for node in nodes:
            self.add_link(node=node)

    def calculate_threshold(self, neighbour):
        """Calculate the threshold at which we consider
        a neighbour is convinced"""
        return self.state.confidence * (1.0 - neighbour.state.confidence)

    def has_different_belief(self, node):
        return (node.state.belief != Belief.NEUTRAL
                and self.state.belief != node.state.belief)

    def get_belief_thresholds(self, nodes, neighbours):
        thresholds = {}
        for name in neighbours:
            neighbour = nodes[name]
            if self.has_different_belief(neighbour):
                belief = str(neighbour.state.belief)
                threshold = self.calculate_threshold(neighbour)
                if not thresholds.get(belief):
                    thresholds[belief] = [threshold]
                else:
                    thresholds[belief].append(threshold)
        return thresholds
