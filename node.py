from dataclasses import dataclass
from enum import Enum, auto
import logging


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
    # I'd rename 'probability' to 'belief_trust_rate' or something like that
    #  to me 'probability' isn't explicit enough
    probability: float

    def __repr__(self):
        return f'{self.belief}: {self.probability}'


class Node:

    def __init__(self, name, state=Belief.NEUTRAL, probability=0.01):
        self.name = name
        self.state = NodeState(state, probability)
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

    def set_belief(self, belief, probability):
        """Set belief
        :param belief: Belief type
        :type belief: Belief
        :param probability: Trust in the belief
        :type probability: float
        """
        self.state.belief = belief
        self.state.probability = probability

    def add_links(self, *nodes):
        """Link current entity with every node"""
        for node in nodes:
            self.add_link(node=node)


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
    prev = get_node_by_name(nodes=prev_nodes, name=node.name)
    return prev.state.belief != node.state.belief


def get_node_by_name(nodes: [Node], name: str):
    """Return node whick name matches parameters name from nodes list
    :param nodes: List of nodes to look into
    :type nodes: list of Node
    :param name: Name of the node to look for
    :type name: str
    :return: Node which name matches parameters
    :rtype: Node
    """
    return list(filter(lambda x: x.name == name, nodes))[0]
