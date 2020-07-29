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

    def calculate_treshold(self, neighbour):
        """Calculate the treshold at which we consider
        a neighbour is convinced"""
        return self.state.confidence * (1.0 - neighbour.state.confidence)

    def has_different_belief(self, node):
        return (node.state.belief != Belief.NEUTRAL
                and self.state.belief != node.state.belief)

    def get_belief_tresholds(self, nodes, neighbours):
        tresholds = {}
        for name in neighbours:
            neighbour = nodes[name]
            if self.has_different_belief(neighbour):
                belief = str(neighbour.state.belief)
                treshold = self.calculate_treshold(neighbour)
                if not tresholds.get(belief):
                    tresholds[belief] = [treshold]
                else:
                    tresholds[belief].append(treshold)
        return tresholds

    def get_next_state_probabilities(self, nodes, neighbours):
        tresholds = self.get_belief_tresholds(nodes, neighbours)

        chances = {}
        for belief in tresholds:
            chances[belief] = functools.reduce(operator.mul, tresholds[belief])

        probabilities = {}
        if len(chances) == 1:
            belief = list(chances.keys())[0]
            probability = list(chances.values())[0]
            # Neighbour wins
            probabilities[belief] = probability
            # Neighbour loses
            probabilities[str(self.state.belief)] = 1 - probability
        elif len(chances) == 2:
            x, y = set(chances.keys())
            # x wins and y loses
            probabilities[x] = chances[x] * (1 - chances[y])
            # y wins and x loses
            probabilities[y] = chances[y] * (1 - chances[x])
            # None wins
            probabilities['remain'] = (1 - chances[x]) * (1 - chances[y])
            # Both win
            probabilities[f"{x}:{y}"] = chances[x] * chances[y]
        return chances, probabilities

    def get_winner(self, chances, probabilities, beliefs):
        x, y = beliefs.split(':')
        treshold = (1 - chances[x]) / (1 - chances[x] + 1 - chances[y])
        r = random_percentage()
        if r <= treshold:
            return x, (chances[x] * probabilities[beliefs])
        return y, (chances[y] * probabilities[beliefs])

    def draw_next_state(self, probabilities):
        choices, weights = list(), list()
        for choice, weight in probabilities.items():
            choices.append(choice)
            weights.append(weight)
        return random.choices(choices, weights=weights, k=1)[0]

    def get_next_state(self, nodes, prev_round_convinced):
        neighbours = prev_round_convinced.intersection(self.neighbours)
        chances, probabilities = self.get_next_state_probabilities(nodes,
                                                                   neighbours)
        if len(chances) > 0 and len(probabilities) > 0:
            next_state = self.draw_next_state(probabilities)
            if ':' in next_state:
                return self.get_winner(chances, probabilities, next_state)
            if 'remain' in next_state or str(self.state.belief) in next_state:
                return None
            return next_state, chances[next_state]
        return None


def get_all_neighours(nodes, names):
    neighbours = set()
    for name in names:
        for neighbour in nodes.get(name).neighbours:
            neighbours.add(neighbour)
    return neighbours
